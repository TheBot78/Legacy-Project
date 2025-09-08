# Copyright (c) 1998-2007 INRIA
# Python rewrite of Geneweb template engine

import os
import re
from typing import Dict, Any, Optional, List, Callable
from jinja2 import Environment, FileSystemLoader, Template
from ..lib.definitions import Person, Family
from ..lib.core.gwdb import Database

class GenewebTemplateEngine:
    """Geneweb template engine for HTML generation"""
    
    def __init__(self, template_dir: str, lang: str = 'en'):
        self.template_dir = template_dir
        self.lang = lang
        self.env = Environment(
            loader=FileSystemLoader(template_dir),
            autoescape=True,
            trim_blocks=True,
            lstrip_blocks=True
        )
        
        # Register custom filters
        self.env.filters['escape_html'] = self._escape_html
        self.env.filters['format_date'] = self._format_date
        self.env.filters['person_link'] = self._person_link
        self.env.filters['family_link'] = self._family_link
    
    def render_person_page(self, person: Person, person_id: int, db: Database, **kwargs) -> str:
        """Render person page"""
        template = self.env.get_template('perso.html')
        
        context = {
            'person': person,
            'person_id': person_id,
            'parents': self._get_parents(person_id, db),
            'families': self._get_families(person_id, db),
            'children': self._get_children(person_id, db),
            'siblings': self._get_siblings(person_id, db),
            'lang': self.lang,
            **kwargs
        }
        
        return template.render(context)
    
    def render_family_page(self, family: Family, family_id: int, db: Database, **kwargs) -> str:
        """Render family page"""
        template = self.env.get_template('family.html')
        
        father = db.get_person(db.get_father(family_id)) if db.get_father(family_id) else None
        mother = db.get_person(db.get_mother(family_id)) if db.get_mother(family_id) else None
        children = [db.get_person(child_id) for child_id in db.get_children(family_id)]
        
        context = {
            'family': family,
            'family_id': family_id,
            'father': father,
            'mother': mother,
            'children': children,
            'lang': self.lang,
            **kwargs
        }
        
        return template.render(context)
    
    def render_search_page(self, query: str, results: List[Dict], **kwargs) -> str:
        """Render search results page"""
        template = self.env.get_template('search.html')
        
        context = {
            'query': query,
            'results': results,
            'total_results': len(results),
            'lang': self.lang,
            **kwargs
        }
        
        return template.render(context)
    
    def render_home_page(self, db: Database, **kwargs) -> str:
        """Render home page"""
        template = self.env.get_template('home.html')
        
        context = {
            'total_persons': db.nb_of_persons(),
            'total_families': db.nb_of_families(),
            'lang': self.lang,
            **kwargs
        }
        
        return template.render(context)
    
    def render_tree_page(self, person_id: int, db: Database, generations: int = 4, **kwargs) -> str:
        """Render family tree page"""
        template = self.env.get_template('tree.html')
        
        tree_data = self._build_tree_data(person_id, db, generations)
        
        context = {
            'person_id': person_id,
            'tree_data': tree_data,
            'generations': generations,
            'lang': self.lang,
            **kwargs
        }
        
        return template.render(context)
    
    def _get_parents(self, person_id: int, db: Database) -> Optional[Dict]:
        """Get person's parents"""
        parents_family = db.get_parents(person_id)
        if not parents_family:
            return None
        
        father_id = db.get_father(parents_family)
        mother_id = db.get_mother(parents_family)
        
        return {
            'father': db.get_person(father_id) if father_id else None,
            'mother': db.get_person(mother_id) if mother_id else None,
            'family_id': parents_family
        }
    
    def _get_families(self, person_id: int, db: Database) -> List[Dict]:
        """Get person's families"""
        family_ids = db.get_family_list(person_id)
        families = []
        
        for family_id in family_ids:
            family = db.get_family(family_id)
            if family:
                father_id = db.get_father(family_id)
                mother_id = db.get_mother(family_id)
                
                # Determine spouse
                spouse_id = mother_id if father_id == person_id else father_id
                spouse = db.get_person(spouse_id) if spouse_id else None
                
                families.append({
                    'family': family,
                    'family_id': family_id,
                    'spouse': spouse,
                    'children': [db.get_person(child_id) for child_id in db.get_children(family_id)]
                })
        
        return families
    
    def _get_children(self, person_id: int, db: Database) -> List[Person]:
        """Get all children of person"""
        children = []
        family_ids = db.get_family_list(person_id)
        
        for family_id in family_ids:
            child_ids = db.get_children(family_id)
            children.extend([db.get_person(child_id) for child_id in child_ids])
        
        return children
    
    def _get_siblings(self, person_id: int, db: Database) -> List[Person]:
        """Get person's siblings"""
        parents_family = db.get_parents(person_id)
        if not parents_family:
            return []
        
        sibling_ids = db.get_children(parents_family)
        return [db.get_person(sibling_id) for sibling_id in sibling_ids if sibling_id != person_id]
    
    def _build_tree_data(self, person_id: int, db: Database, generations: int) -> Dict:
        """Build tree data for visualization"""
        def build_ancestors(pid: int, gen: int) -> Dict:
            if gen <= 0 or not pid:
                return None
            
            person = db.get_person(pid)
            if not person:
                return None
            
            parents = self._get_parents(pid, db)
            
            return {
                'person': person,
                'person_id': pid,
                'generation': generations - gen + 1,
                'father': build_ancestors(parents['father'].key_index if parents and parents['father'] else None, gen - 1),
                'mother': build_ancestors(parents['mother'].key_index if parents and parents['mother'] else None, gen - 1)
            }
        
        return build_ancestors(person_id, generations)
    
    def _escape_html(self, text: str) -> str:
        """Escape HTML characters"""
        return (text.replace('&', '&amp;')
                   .replace('<', '&lt;')
                   .replace('>', '&gt;')
                   .replace('"', '&quot;')
                   .replace("'", '&#x27;'))
    
    def _format_date(self, date_obj) -> str:
        """Format date for display"""
        if not date_obj:
            return ""
        
        if hasattr(date_obj, 'text') and date_obj.text:
            return date_obj.text
        
        if hasattr(date_obj, 'dmy') and date_obj.dmy:
            dmy = date_obj.dmy
            return f"{dmy.day:02d}/{dmy.month:02d}/{dmy.year}"
        
        return str(date_obj)
    
    def _person_link(self, person: Person, person_id: int) -> str:
        """Generate person link"""
        if not person:
            return ""
        
        name = f"{person.first_name} {person.surname}"
        return f'<a href="/person?id={person_id}">{self._escape_html(name)}</a>'
    
    def _family_link(self, family_id: int) -> str:
        """Generate family link"""
        return f'<a href="/family?id={family_id}">Family {family_id}</a>'

# Template files content
TEMPLATE_FILES = {
    'base.html': '''
<!DOCTYPE html>
<html lang="{{ lang }}">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>{% block title %}Geneweb{% endblock %}</title>
    <link rel="stylesheet" href="/static/css/geneweb.css">
    {% block head %}{% endblock %}
</head>
<body>
    <nav class="navbar">
        <div class="nav-brand">
            <a href="/">Geneweb</a>
        </div>
        <div class="nav-menu">
            <a href="/">Home</a>
            <a href="/search">Search</a>
            <a href="/stats">Statistics</a>
        </div>
    </nav>
    
    <main class="container">
        {% block content %}{% endblock %}
    </main>
    
    <footer>
        <p>&copy; 2024 Geneweb - Genealogy Database</p>
    </footer>
    
    <script src="/static/js/geneweb.js"></script>
    {% block scripts %}{% endblock %}
</body>
</html>
''',
    
    'home.html': '''
{% extends "base.html" %}

{% block title %}Geneweb - Home{% endblock %}

{% block content %}
<div class="hero">
    <h1>Welcome to Geneweb</h1>
    <p>Explore your family history</p>
</div>

<div class="stats-grid">
    <div class="stat-card">
        <h3>{{ total_persons }}</h3>
        <p>Persons</p>
    </div>
    <div class="stat-card">
        <h3>{{ total_families }}</h3>
        <p>Families</p>
    </div>
</div>

<div class="quick-actions">
    <a href="/search" class="btn btn-primary">Search Persons</a>
    <a href="/person?id=1" class="btn btn-secondary">Browse</a>
</div>
{% endblock %}
''',
    
    'perso.html': '''
{% extends "base.html" %}

{% block title %}{{ person.first_name }} {{ person.surname }}{% endblock %}

{% block content %}
<div class="person-header">
    <h1>{{ person.first_name }} {{ person.surname }}</h1>
    {% if person.occ > 0 %}
        <span class="occurrence">({{ person.occ }})</span>
    {% endif %}
</div>

<div class="person-details">
    <div class="basic-info">
        <h2>Basic Information</h2>
        <dl>
            <dt>Sex:</dt>
            <dd>{{ person.sex.value|title }}</dd>
            
            {% if person.birth %}
            <dt>Birth:</dt>
            <dd>{{ person.birth|format_date }}
                {% if person.birth_place %} in {{ person.birth_place }}{% endif %}
            </dd>
            {% endif %}
            
            {% if person.death %}
            <dt>Death:</dt>
            <dd>{{ person.death.date|format_date if person.death.date else person.death.status.value|title }}
                {% if person.death_place %} in {{ person.death_place }}{% endif %}
            </dd>
            {% endif %}
            
            {% if person.occupation %}
            <dt>Occupation:</dt>
            <dd>{{ person.occupation }}</dd>
            {% endif %}
        </dl>
    </div>
    
    {% if parents %}
    <div class="parents">
        <h2>Parents</h2>
        <ul>
            {% if parents.father %}
            <li>Father: {{ parents.father|person_link(parents.father.key_index)|safe }}</li>
            {% endif %}
            {% if parents.mother %}
            <li>Mother: {{ parents.mother|person_link(parents.mother.key_index)|safe }}</li>
            {% endif %}
        </ul>
    </div>
    {% endif %}
    
    {% if families %}
    <div class="families">
        <h2>Families</h2>
        {% for family_info in families %}
        <div class="family">
            <h3>{{ family_info.family_id|family_link|safe }}</h3>
            {% if family_info.spouse %}
            <p>Spouse: {{ family_info.spouse|person_link(family_info.spouse.key_index)|safe }}</p>
            {% endif %}
            
            {% if family_info.family.marriage %}
            <p>Marriage: {{ family_info.family.marriage|format_date }}</p>
            {% endif %}
            
            {% if family_info.children %}
            <h4>Children:</h4>
            <ul>
                {% for child in family_info.children %}
                <li>{{ child|person_link(child.key_index)|safe }}</li>
                {% endfor %}
            </ul>
            {% endif %}
        </div>
        {% endfor %}
    </div>
    {% endif %}
</div>

<div class="actions">
    <a href="/tree?id={{ person_id }}" class="btn btn-primary">View Tree</a>
    <a href="/edit/person?id={{ person_id }}" class="btn btn-secondary">Edit</a>
</div>
{% endblock %}
'''
}

def create_template_files(template_dir: str):
    """Create template files"""
    os.makedirs(template_dir, exist_ok=True)
    
    for filename, content in TEMPLATE_FILES.items():
        filepath = os.path.join(template_dir, filename)
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
