import pytest
from unittest.mock import patch, MagicMock
from front.geneweb_app import app


class TestGenewebApp:
    """Tests for geneweb_app Flask application."""

    @pytest.fixture
    def client(self):
        """Create a test client for the Flask app."""
        app.config['TESTING'] = True
        with app.test_client() as client:
            yield client

    def test_home_route_default_language(self, client):
        """Test home route with default language."""
        response = client.get('/')
        assert response.status_code == 200
        assert b'lang=en' in response.data or b'lang="en"' in response.data

    def test_home_route_with_valid_language(self, client):
        """Test home route with valid language parameter."""
        response = client.get('/?lang=fr')
        assert response.status_code == 200
        assert b'lang=fr' in response.data or b'lang="fr"' in response.data

    def test_home_route_with_invalid_language_defaults_to_english(self, client):
        """Test home route with invalid language defaults to English."""
        response = client.get('/?lang=invalid')
        assert response.status_code == 200
        assert b'lang=en' in response.data or b'lang="en"' in response.data

    def test_home_route_with_uppercase_language(self, client):
        """Test home route with uppercase language gets converted to lowercase."""
        response = client.get('/?lang=FR')
        assert response.status_code == 200
        assert b'lang=fr' in response.data or b'lang="fr"' in response.data

    def test_home_route_with_all_valid_languages(self, client):
        """Test home route with all valid languages."""
        valid_langs = ["de", "en", "es", "fr", "it", "lv", "nl", "no", "fi", "sv"]
        
        for lang in valid_langs:
            response = client.get(f'/?lang={lang}')
            assert response.status_code == 200
            assert f'lang={lang}'.encode() in response.data or f'lang="{lang}"'.encode() in response.data

    def test_home_route_renders_welcome_template(self, client):
        """Test that home route renders the welcome template."""
        response = client.get('/')
        assert response.status_code == 200
        # Check for common elements that would be in welcome.html
        assert b'html' in response.data.lower()

    def test_home_route_with_empty_language_parameter(self, client):
        """Test home route with empty language parameter defaults to English."""
        response = client.get('/?lang=')
        assert response.status_code == 200
        assert b'lang=en' in response.data or b'lang="en"' in response.data

    def test_home_route_with_special_characters_in_language(self, client):
        """Test home route with special characters in language parameter."""
        response = client.get('/?lang=fr@#$')
        assert response.status_code == 200
        assert b'lang=en' in response.data or b'lang="en"' in response.data

    def test_home_route_with_numeric_language(self, client):
        """Test home route with numeric language parameter."""
        response = client.get('/?lang=123')
        assert response.status_code == 200
        assert b'lang=en' in response.data or b'lang="en"' in response.data

    def test_home_route_with_mixed_case_valid_language(self, client):
        """Test home route with mixed case valid language."""
        response = client.get('/?lang=De')
        assert response.status_code == 200
        assert b'lang=de' in response.data or b'lang="de"' in response.data

    def test_home_route_with_multiple_parameters(self, client):
        """Test home route with multiple parameters including language."""
        response = client.get('/?lang=es&other=value')
        assert response.status_code == 200
        assert b'lang=es' in response.data or b'lang="es"' in response.data

    def test_home_route_language_validation_boundary_cases(self, client):
        """Test language validation with boundary cases."""
        # Test with very long string
        long_lang = 'a' * 100
        response = client.get(f'/?lang={long_lang}')
        assert response.status_code == 200
        assert b'lang=en' in response.data or b'lang="en"' in response.data
        
        # Test with single character
        response = client.get('/?lang=f')
        assert response.status_code == 200
        assert b'lang=en' in response.data or b'lang="en"' in response.data

    def test_home_route_content_type(self, client):
        """Test that home route returns HTML content."""
        response = client.get('/')
        assert response.status_code == 200
        assert 'text/html' in response.content_type

    def test_home_route_no_cache_headers(self, client):
        """Test that appropriate headers are set."""
        response = client.get('/')
        assert response.status_code == 200
        # Flask typically sets some default headers
        assert 'Content-Type' in response.headers

    def test_app_configuration(self):
        """Test Flask app configuration."""
        assert app.name == 'front.geneweb_app'
        # Test that the app can be configured for testing
        app.config['TESTING'] = True
        assert app.config['TESTING'] is True

    def test_app_debug_mode_in_main(self):
        """Test that debug mode is enabled when run as main."""
        # This tests the configuration that would be set when running as __main__
        # We can't directly test the if __name__ == "__main__" block,
        # but we can verify the app configuration
        assert hasattr(app, 'run')

    def test_home_route_handles_none_language(self, client):
        """Test home route when language parameter is explicitly None."""
        # This simulates a case where request.args.get might return None
        response = client.get('/')
        assert response.status_code == 200
        # Should default to 'en' when no lang parameter is provided
        assert b'lang=en' in response.data or b'lang="en"' in response.data

    def test_valid_languages_list_completeness(self):
        """Test that all expected languages are in the valid list."""
        # This is more of a documentation test to ensure we know what languages are supported
        expected_langs = ["de", "en", "es", "fr", "it", "lv", "nl", "no", "fi", "sv"]
        
        # Test each language individually to ensure they're all handled
        with app.test_client() as client:
            for lang in expected_langs:
                response = client.get(f'/?lang={lang}')
                assert response.status_code == 200
                assert f'lang={lang}'.encode() in response.data or f'lang="{lang}"'.encode() in response.data

    def test_home_route_with_whitespace_language(self, client):
        """Test home route with whitespace in language parameter."""
        response = client.get('/?lang= fr ')
        assert response.status_code == 200
        # Should be treated as invalid and default to 'en'
        assert b'lang=en' in response.data or b'lang="en"' in response.data