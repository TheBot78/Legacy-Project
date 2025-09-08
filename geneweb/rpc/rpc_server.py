# Copyright (c) 1998-2007 INRIA
# Python rewrite of Geneweb RPC API

import json
from typing import Dict, Any, List, Optional, Callable
from dataclasses import asdict
from flask import Flask, request, jsonify
from ..lib.core.gwdb import Database, open_database
from ..lib.definitions import Person, Family, Sex, Access
from ..lib.util.name import name_equiv

class GenewebRPCServer:
    """Geneweb RPC API Server"""
    
    def __init__(self, database_dir: str, host: str = 'localhost', port: int = 2318):
        self.database_dir = database_dir
        self.host = host
        self.port = port
        self.app = Flask(__name__)
        self.db: Optional[Database] = None
        
        # Register RPC methods
        self._register_routes()
    
    def _register_routes(self):
        """Register RPC API routes"""
        
        @self.app.route('/api/person/<int:person_id>', methods=['GET'])
        def get_person(person_id: int):
            """Get person by ID"""
            try:
                person = self.db.get_person(person_id)
                if person:
                    return jsonify({
                        'success': True,
                        'data': self._person_to_dict(person, person_id)
                    })
                else:
                    return jsonify({
                        'success': False,
                        'error': 'Person not found'
                    }), 404
            except Exception as e:
                return jsonify({
                    'success': False,
                    'error': str(e)
                }), 500
        
        @self.app.route('/api/person', methods=['POST'])
        def create_person():
            """Create new person"""
            try:
                data = request.get_json()
                person = self._dict_to_person(data)
                
                # Find next available ID
                person_id = self.db.nb_of_persons()
                self.db.set_person(person_id, person)
                self.db.commit_patches()
                
                return jsonify({
                    'success': True,
                    'data': {
                        'person_id': person_id,
                        'person': self._person_to_dict(person, person_id)
                    }
                }), 201
            except Exception as e:
                return jsonify({
                    'success': False,
                    'error': str(e)
                }), 500
        
        @self.app.route('/api/person/<int:person_id>', methods=['PUT'])
        def update_person(person_id: int):
            """Update person"""
            try:
                data = request.get_json()
                person = self._dict_to_person(data)
                
                self.db.set_person(person_id, person)
                self.db.commit_patches()
                
                return jsonify({
                    'success': True,
                    'data': self._person_to_dict(person, person_id)
                })
            except Exception as e:
                return jsonify({
                    'success': False,
                    'error': str(e)
                }), 500
        
        @self.app.route('/api/family/<int:family_id>', methods=['GET'])
        def get_family(family_id: int):
            """Get family by ID"""
            try:
                family = self.db.get_family(family_id)
                if family:
                    return jsonify({
                        'success': True,
                        'data': self._family_to_dict(family, family_id)
                    })
                else:
                    return jsonify({
                        'success': False,
                        'error': 'Family not found'
                    }), 404
            except Exception as e:
                return jsonify({
                    'success': False,
                    'error': str(e)
                }), 500
        
        @self.app.route('/api/search/person', methods=['GET'])
        def search_persons():
            """Search persons"""
            try:
                query = request.args.get('q', '')
                limit = int(request.args.get('limit', 50))
                
                results = self._search_persons(query, limit)
                
                return jsonify({
                    'success': True,
                    'data': {
                        'query': query,
                        'results': results,
                        'total': len(results)
                    }
                })
            except Exception as e:
                return jsonify({
                    'success': False,
                    'error': str(e)
                }), 500
        
        @self.app.route('/api/tree/<int:person_id>', methods=['GET'])
        def get_tree(person_id: int):
            """Get family tree"""
            try:
                generations = int(request.args.get('generations', 4))
                tree_data = self._build_tree(person_id, generations)
                
                return jsonify({
                    'success': True,
                    'data': tree_data
                })
            except Exception as e:
                return jsonify({
                    'success': False,
                    'error': str(e)
                }), 500
        
        @self.app.route('/api/stats', methods=['GET'])
        def get_stats():
            """Get database statistics"""
            try:
                stats = {
                    'total_persons': self.db.nb_of_persons(),
                    'total_families': self.db.nb_of_families(),
                    'males': 0,
                    'females': 0,
                    'unknown_sex': 0
                }
                
                # Count by sex
                for i in range(self.db.nb_of_persons()):
                    person = self.db.get_person(i)
                    if person:
                        if person.sex == Sex.MALE:
                            stats['males'] += 1
                        elif person.sex == Sex.FEMALE:
                            stats['females'] += 1
                        else:
                            stats['unknown_sex'] += 1
                
                return jsonify({
                    'success': True,
                    'data': stats
                })
            except Exception as e:
                return jsonify({
                    'success': False,
                    'error': str(e)
                }), 500
    
    def _person_to_dict(self, person: Person, person_id: int) -> Dict[str, Any]:
        """Convert person to dictionary"""
        result = asdict(person)
        result['person_id'] = person_id
        
        # Convert enums to strings
        if 'sex' in result:
            result['sex'] = person.sex.value
        if 'access' in result:
            result['access'] = person.access.value
        
        # Convert dates
        if person.birth:
            result['birth'] = str(person.birth)
        if person.death:
            result['death'] = {
                'status': person.death.status.value,
                'date': str(person.death.date) if person.death.date else None,
                'reason': person.death.reason.value if person.death.reason else None
            }
        
        return result
    
    def _dict_to_person(self, data: Dict[str, Any]) -> Person:
        """Convert dictionary to person"""
        person = Person()
        
        # Basic fields
        person.first_name = data.get('first_name', '')
        person.surname = data.get('surname', '')
        person.occ = data.get('occ', 0)
        person.image = data.get('image', '')
        person.public_name = data.get('public_name', '')
        person.occupation = data.get('occupation', '')
        
        # Sex
        sex_str = data.get('sex', 'neuter')
        person.sex = Sex(sex_str) if sex_str in [s.value for s in Sex] else Sex.NEUTER
        
        # Access
        access_str = data.get('access', 'private')
        person.access = Access(access_str) if access_str in [a.value for a in Access] else Access.PRIVATE
        
        # Places and notes
        person.birth_place = data.get('birth_place', '')
        person.death_place = data.get('death_place', '')
        person.notes = data.get('notes', '')
        
        return person
    
    def _family_to_dict(self, family: Family, family_id: int) -> Dict[str, Any]:
        """Convert family to dictionary"""
        result = asdict(family)
        result['family_id'] = family_id
        
        # Get family members
        father_id = self.db.get_father(family_id)
        mother_id = self.db.get_mother(family_id)
        children_ids = self.db.get_children(family_id)
        
        result['father'] = self._person_to_dict(self.db.get_person(father_id), father_id) if father_id else None
        result['mother'] = self._person_to_dict(self.db.get_person(mother_id), mother_id) if mother_id else None
        result['children'] = [self._person_to_dict(self.db.get_person(child_id), child_id) 
                             for child_id in children_ids if self.db.get_person(child_id)]
        
        return result
    
    def _search_persons(self, query: str, limit: int) -> List[Dict[str, Any]]:
        """Search persons by name"""
        results = []
        query_lower = query.lower()
        
        for i in range(min(self.db.nb_of_persons(), limit * 10)):  # Search more to filter
            person = self.db.get_person(i)
            if person:
                full_name = f"{person.first_name} {person.surname}".lower()
                if (query_lower in full_name or 
                    name_equiv(query, person.first_name) or 
                    name_equiv(query, person.surname)):
                    results.append(self._person_to_dict(person, i))
                    
                    if len(results) >= limit:
                        break
        
        return results
    
    def _build_tree(self, person_id: int, generations: int) -> Dict[str, Any]:
        """Build family tree data"""
        def build_ancestors(pid: int, gen: int) -> Optional[Dict[str, Any]]:
            if gen <= 0 or not pid:
                return None
            
            person = self.db.get_person(pid)
            if not person:
                return None
            
            parents_family = self.db.get_parents(pid)
            father_id = self.db.get_father(parents_family) if parents_family else None
            mother_id = self.db.get_mother(parents_family) if parents_family else None
            
            return {
                'person': self._person_to_dict(person, pid),
                'generation': generations - gen + 1,
                'father': build_ancestors(father_id, gen - 1) if father_id else None,
                'mother': build_ancestors(mother_id, gen - 1) if mother_id else None
            }
        
        return build_ancestors(person_id, generations)
    
    def start(self):
        """Start RPC server"""
        self.db = open_database(self.database_dir)
        print(f"Geneweb RPC server starting on http://{self.host}:{self.port}")
        self.app.run(host=self.host, port=self.port, debug=False)
    
    def stop(self):
        """Stop RPC server"""
        if self.db:
            self.db.close()

def main():
    """Main function for RPC server"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Geneweb RPC Server')
    parser.add_argument('-p', '--port', type=int, default=2318, help='Port number')
    parser.add_argument('-a', '--addr', default='localhost', help='Address to bind')
    parser.add_argument('-d', '--database', default='./base', help='Database directory')
    
    args = parser.parse_args()
    
    server = GenewebRPCServer(args.database, args.addr, args.port)
    try:
        server.start()
    except KeyboardInterrupt:
        print("\nShutting down RPC server...")
        server.stop()

if __name__ == '__main__':
    main()
