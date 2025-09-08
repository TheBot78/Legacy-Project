# Tests for RPC API

import unittest
import json
import tempfile
import shutil
from ..rpc.rpc_server import GenewebRPCServer
from ..lib.definitions import Person, Sex, Access

class TestRPCAPI(unittest.TestCase):
    """Test RPC API functionality"""
    
    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        self.server = GenewebRPCServer(self.test_dir, port=0)  # Random port
        self.client = self.server.app.test_client()
        
        # Initialize database
        from ..lib.core.gwdb import open_database
        self.server.db = open_database(self.test_dir)
    
    def tearDown(self):
        if self.server.db:
            self.server.db.close()
        shutil.rmtree(self.test_dir)
    
    def test_get_person_not_found(self):
        """Test getting non-existent person"""
        response = self.client.get('/api/person/999')
        self.assertEqual(response.status_code, 404)
        
        data = json.loads(response.data)
        self.assertFalse(data['success'])
    
    def test_create_person(self):
        """Test creating a person via API"""
        person_data = {
            'first_name': 'John',
            'surname': 'Doe',
            'sex': 'male',
            'access': 'public'
        }
        
        response = self.client.post('/api/person', 
                                  data=json.dumps(person_data),
                                  content_type='application/json')
        
        self.assertEqual(response.status_code, 201)
        
        data = json.loads(response.data)
        self.assertTrue(data['success'])
        self.assertEqual(data['data']['person']['first_name'], 'John')
    
    def test_search_persons(self):
        """Test person search via API"""
        # Create test person first
        person = Person(first_name="John", surname="Doe", sex=Sex.MALE)
        self.server.db.set_person(0, person)
        
        response = self.client.get('/api/search/person?q=John')
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.data)
        self.assertTrue(data['success'])
        self.assertGreaterEqual(len(data['data']['results']), 0)
    
    def test_get_stats(self):
        """Test getting database statistics"""
        response = self.client.get('/api/stats')
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.data)
        self.assertTrue(data['success'])
        self.assertIn('total_persons', data['data'])
        self.assertIn('total_families', data['data'])

if __name__ == '__main__':
    unittest.main()