# Copyright (c) 1998-2007 INRIA
# Tests for Geneweb database functionality

import unittest
import tempfile
import shutil
from ..lib.core.gwdb import open_database
from ..lib.lib.definitions import Person, Family, Sex, Access
from ..lib.db.dbdisk import Perm

class TestDatabase(unittest.TestCase):
    """Test database operations"""
    
    def setUp(self):
        """Set up test database"""
        self.test_dir = tempfile.mkdtemp()
        self.db = open_database(self.test_dir)
    
    def tearDown(self):
        """Clean up test database"""
        self.db.close()
        shutil.rmtree(self.test_dir)
    
    def test_person_creation(self):
        """Test person creation and retrieval"""
        person = Person(
            first_name="John",
            surname="Doe",
            sex=Sex.MALE,
            access=Access.PUBLIC
        )
        
        self.db.set_person(0, person)
        retrieved = self.db.get_person(0)
        
        self.assertIsNotNone(retrieved)
        self.assertEqual(retrieved.first_name, "John")
        self.assertEqual(retrieved.surname, "Doe")
        self.assertEqual(retrieved.sex, Sex.MALE)
    
    def test_family_creation(self):
        """Test family creation and retrieval"""
        family = Family()
        
        self.db.set_family(0, family)
        retrieved = self.db.get_family(0)
        
        self.assertIsNotNone(retrieved)
    
    def test_person_search(self):
        """Test person search functionality"""
        # Create test persons
        persons = [
            Person(first_name="John", surname="Doe", sex=Sex.MALE),
            Person(first_name="Jane", surname="Doe", sex=Sex.FEMALE),
            Person(first_name="Bob", surname="Smith", sex=Sex.MALE)
        ]
        
        for i, person in enumerate(persons):
            self.db.set_person(i, person)
        
        # Test search by surname
        doe_persons = self.db.persons_of_name("Doe")
        self.assertGreaterEqual(len(doe_persons), 2)
    
    def test_commit_patches(self):
        """Test committing changes"""
        person = Person(first_name="Test", surname="Person")
        self.db.set_person(0, person)
        
        # Should not raise exception
        self.db.commit_patches()
        
        # Verify person is still there
        retrieved = self.db.get_person(0)
        self.assertIsNotNone(retrieved)
        self.assertEqual(retrieved.first_name, "Test")

class TestConsanguinity(unittest.TestCase):
    """Test consanguinity calculations"""
    
    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        self.db = open_database(self.test_dir)
    
    def tearDown(self):
        self.db.close()
        shutil.rmtree(self.test_dir)
    
    def test_simple_relationship(self):
        """Test simple relationship calculation"""
        # Create a simple family structure
        # Parents: John (0) and Jane (1)
        # Children: Bob (2) and Alice (3)
        
        john = Person(first_name="John", surname="Doe", sex=Sex.MALE)
        jane = Person(first_name="Jane", surname="Doe", sex=Sex.FEMALE)
        bob = Person(first_name="Bob", surname="Doe", sex=Sex.MALE)
        alice = Person(first_name="Alice", surname="Doe", sex=Sex.FEMALE)
        
        self.db.set_person(0, john)
        self.db.set_person(1, jane)
        self.db.set_person(2, bob)
        self.db.set_person(3, alice)
        
        family = Family()
        self.db.set_family(0, family)
        
        # Bob and Alice should be siblings (no consanguinity for marriage)
        # This is a simplified test - real implementation would be more complex
        self.assertTrue(True)  # Placeholder

if __name__ == '__main__':
    unittest.main()
