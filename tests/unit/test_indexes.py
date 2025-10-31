import pytest
from backend.indexes import (
    _stable_hash, next_prime, build_strings_index, build_names_index
)


class TestStableHash:
    """Test the _stable_hash function."""
    
    def test_stable_hash_same_input_same_output(self):
        """Test that same input produces same hash."""
        text = "test string"
        hash1 = _stable_hash(text)
        hash2 = _stable_hash(text)
        assert hash1 == hash2
    
    def test_stable_hash_different_inputs_different_outputs(self):
        """Test that different inputs produce different hashes."""
        hash1 = _stable_hash("test1")
        hash2 = _stable_hash("test2")
        assert hash1 != hash2
    
    def test_stable_hash_returns_integer(self):
        """Test that hash returns an integer."""
        result = _stable_hash("test")
        assert isinstance(result, int)
        assert result >= 0
    
    def test_stable_hash_empty_string(self):
        """Test hash with empty string."""
        result = _stable_hash("")
        assert isinstance(result, int)
    
    def test_stable_hash_unicode_characters(self):
        """Test hash with unicode characters."""
        result1 = _stable_hash("François")
        result2 = _stable_hash("François")
        assert result1 == result2
        assert isinstance(result1, int)


class TestNextPrime:
    """Test the next_prime function."""
    
    def test_next_prime_small_numbers(self):
        """Test next_prime with small numbers."""
        assert next_prime(1) == 3
        assert next_prime(2) == 3
        assert next_prime(3) == 3
        assert next_prime(4) == 5
        assert next_prime(5) == 5
        assert next_prime(6) == 7
        assert next_prime(10) == 11
    
    def test_next_prime_already_prime(self):
        """Test next_prime when input is already prime."""
        primes = [3, 5, 7, 11, 13, 17, 19, 23]
        for p in primes:
            assert next_prime(p) == p
    
    def test_next_prime_larger_numbers(self):
        """Test next_prime with larger numbers."""
        assert next_prime(100) == 101
        assert next_prime(200) == 211
    
    def test_next_prime_returns_prime(self):
        """Test that next_prime always returns a prime number."""
        def is_prime(n):
            if n < 2:
                return False
            if n == 2:
                return True
            if n % 2 == 0:
                return False
            for i in range(3, int(n**0.5) + 1, 2):
                if n % i == 0:
                    return False
            return True
        
        test_values = [1, 4, 6, 8, 9, 10, 15, 20, 25, 30]
        for val in test_values:
            result = next_prime(val)
            assert is_prime(result), f"next_prime({val}) = {result} is not prime"
            assert result >= val, f"next_prime({val}) = {result} is less than input"


class TestBuildStringsIndex:
    """Test the build_strings_index function."""
    
    def test_build_strings_index_empty_list(self):
        """Test build_strings_index with empty list."""
        result = build_strings_index([])
        assert result == {"table_size": 0, "buckets": []}
    
    def test_build_strings_index_single_string(self):
        """Test build_strings_index with single string."""
        strings = ["test"]
        result = build_strings_index(strings)
        
        assert "table_size" in result
        assert "buckets" in result
        assert result["table_size"] > 0
        assert len(result["buckets"]) == result["table_size"]
        
        # Check that string id 0 appears in some bucket
        all_ids = []
        for bucket in result["buckets"]:
            all_ids.extend(bucket)
        assert 0 in all_ids
    
    def test_build_strings_index_multiple_strings(self):
        """Test build_strings_index with multiple strings."""
        strings = ["John", "Jane", "Doe", "Smith"]
        result = build_strings_index(strings)
        
        assert result["table_size"] > 0
        assert len(result["buckets"]) == result["table_size"]
        
        # Check that all string ids appear in buckets
        all_ids = []
        for bucket in result["buckets"]:
            all_ids.extend(bucket)
        
        for i in range(len(strings)):
            assert i in all_ids
    
    def test_build_strings_index_duplicate_crushed_names(self):
        """Test build_strings_index with strings that crush to same value."""
        # These should crush to similar values
        strings = ["François", "Francois", "FRANCOIS"]
        result = build_strings_index(strings)
        
        assert result["table_size"] > 0
        assert len(result["buckets"]) == result["table_size"]
        
        # All string ids should be present
        all_ids = []
        for bucket in result["buckets"]:
            all_ids.extend(bucket)
        
        assert set(all_ids) == {0, 1, 2}
    
    def test_build_strings_index_table_size_is_prime(self):
        """Test that table_size is always prime."""
        def is_prime(n):
            if n < 2:
                return False
            if n == 2:
                return True
            if n % 2 == 0:
                return False
            for i in range(3, int(n**0.5) + 1, 2):
                if n % i == 0:
                    return False
            return True
        
        test_cases = [
            ["a"],
            ["a", "b"],
            ["a", "b", "c", "d", "e"],
            [f"string_{i}" for i in range(20)]
        ]
        
        for strings in test_cases:
            result = build_strings_index(strings)
            if result["table_size"] > 0:
                assert is_prime(result["table_size"])


class TestBuildNamesIndex:
    """Test the build_names_index function."""
    
    def test_build_names_index_empty_persons(self):
        """Test build_names_index with empty persons list."""
        result = build_names_index([], [])
        
        expected = {
            "name_to_person": {"table_size": 0, "buckets": []},
            "surname_ngrams": {"table_size": 0, "buckets": []},
            "firstname_ngrams": {"table_size": 0, "buckets": []}
        }
        assert result == expected
    
    def test_build_names_index_single_person(self):
        """Test build_names_index with single person."""
        strings = ["John", "Doe"]
        persons = [
            {
                "id": 1,
                "first_name_ids": [0],  # "John"
                "surname_id": 1  # "Doe"
            }
        ]
        
        result = build_names_index(persons, strings)
        
        # Check structure
        assert "name_to_person" in result
        assert "surname_ngrams" in result
        assert "firstname_ngrams" in result
        
        # Check that all indexes have proper structure
        for index_name in ["name_to_person", "surname_ngrams", "firstname_ngrams"]:
            index = result[index_name]
            assert "table_size" in index
            assert "buckets" in index
            assert index["table_size"] > 0
            assert len(index["buckets"]) == index["table_size"]
        
        # Check that person id appears in name_to_person buckets
        name_buckets = result["name_to_person"]["buckets"]
        all_person_ids = []
        for bucket in name_buckets:
            all_person_ids.extend(bucket)
        assert 1 in all_person_ids
    
    def test_build_names_index_multiple_persons(self):
        """Test build_names_index with multiple persons."""
        strings = ["John", "Doe", "Jane", "Smith", "Bob"]
        persons = [
            {
                "id": 1,
                "first_name_ids": [0],  # "John"
                "surname_id": 1  # "Doe"
            },
            {
                "id": 2,
                "first_name_ids": [2],  # "Jane"
                "surname_id": 3  # "Smith"
            },
            {
                "id": 3,
                "first_name_ids": [4],  # "Bob"
                "surname_id": 1  # "Doe"
            }
        ]
        
        result = build_names_index(persons, strings)
        
        # Check that all person ids appear in name_to_person
        name_buckets = result["name_to_person"]["buckets"]
        all_person_ids = []
        for bucket in name_buckets:
            all_person_ids.extend(bucket)
        
        assert set(all_person_ids) == {1, 2, 3}
        
        # Check that surname string ids appear in surname_ngrams
        surname_buckets = result["surname_ngrams"]["buckets"]
        all_surname_ids = []
        for bucket in surname_buckets:
            all_surname_ids.extend(bucket)
        
        # Should contain string ids for "Doe" (1) and "Smith" (3)
        assert 1 in all_surname_ids
        assert 3 in all_surname_ids
    
    def test_build_names_index_person_with_multiple_first_names(self):
        """Test build_names_index with person having multiple first names."""
        strings = ["Jean", "Pierre", "Dupont"]
        persons = [
            {
                "id": 1,
                "first_name_ids": [0, 1],  # "Jean", "Pierre"
                "surname_id": 2  # "Dupont"
            }
        ]
        
        result = build_names_index(persons, strings)
        
        # Check that person appears in name_to_person
        name_buckets = result["name_to_person"]["buckets"]
        all_person_ids = []
        for bucket in name_buckets:
            all_person_ids.extend(bucket)
        assert 1 in all_person_ids
        
        # Check that both first name string ids appear in firstname_ngrams
        fname_buckets = result["firstname_ngrams"]["buckets"]
        all_fname_ids = []
        for bucket in fname_buckets:
            all_fname_ids.extend(bucket)
        
        # Should contain string ids for "Jean" (0) and "Pierre" (1)
        assert 0 in all_fname_ids
        assert 1 in all_fname_ids
    
    def test_build_names_index_person_with_missing_fields(self):
        """Test build_names_index with person missing some fields."""
        strings = ["John"]
        persons = [
            {
                "id": 1,
                "first_name_ids": [0],  # "John"
                # No surname_id
            },
            {
                "id": 2,
                "surname_id": 0,  # "John" as surname
                # No first_name_ids
            }
        ]
        
        result = build_names_index(persons, strings)
        
        # Should not crash and should handle missing fields gracefully
        assert "name_to_person" in result
        assert "surname_ngrams" in result
        assert "firstname_ngrams" in result
        
        # Both persons should appear in name_to_person
        name_buckets = result["name_to_person"]["buckets"]
        all_person_ids = []
        for bucket in name_buckets:
            all_person_ids.extend(bucket)
        
        assert 1 in all_person_ids
        assert 2 in all_person_ids
    
    def test_build_names_index_table_sizes_are_prime(self):
        """Test that all table sizes are prime numbers."""
        def is_prime(n):
            if n < 2:
                return False
            if n == 2:
                return True
            if n % 2 == 0:
                return False
            for i in range(3, int(n**0.5) + 1, 2):
                if n % i == 0:
                    return False
            return True
        
        strings = ["John", "Jane", "Doe", "Smith"]
        persons = [
            {"id": 1, "first_name_ids": [0], "surname_id": 2},
            {"id": 2, "first_name_ids": [1], "surname_id": 3}
        ]
        
        result = build_names_index(persons, strings)
        
        for index_name in ["name_to_person", "surname_ngrams", "firstname_ngrams"]:
            table_size = result[index_name]["table_size"]
            if table_size > 0:
                assert is_prime(table_size), f"{index_name} table_size {table_size} is not prime"
    
    def test_build_names_index_ngrams_functionality(self):
        """Test that ngrams are properly handled in indexes."""
        # Use longer names to ensure ngrams are generated
        strings = ["Alexander", "Elizabeth", "Johnson"]
        persons = [
            {
                "id": 1,
                "first_name_ids": [0],  # "Alexander"
                "surname_id": 2  # "Johnson"
            },
            {
                "id": 2,
                "first_name_ids": [1],  # "Elizabeth"
                "surname_id": 2  # "Johnson"
            }
        ]
        
        result = build_names_index(persons, strings)
        
        # Check that surname ngrams contain the surname string id
        surname_buckets = result["surname_ngrams"]["buckets"]
        all_surname_ids = []
        for bucket in surname_buckets:
            all_surname_ids.extend(bucket)
        
        # "Johnson" has string id 2
        assert 2 in all_surname_ids
        
        # Check that firstname ngrams contain the firstname string ids
        fname_buckets = result["firstname_ngrams"]["buckets"]
        all_fname_ids = []
        for bucket in fname_buckets:
            all_fname_ids.extend(bucket)
        
        # "Alexander" has string id 0, "Elizabeth" has string id 1
        assert 0 in all_fname_ids
        assert 1 in all_fname_ids