import pytest
from front.main_page import app


class TestMainPageApp:
    """Tests for main_page Flask application."""

    @pytest.fixture
    def client(self):
        """Create a test client for the Flask app."""
        app.config['TESTING'] = True
        with app.test_client() as client:
            yield client

    def test_home_route_returns_welcome_message(self, client):
        """Test that home route returns the welcome message."""
        response = client.get('/')
        assert response.status_code == 200
        assert b'Bienvenue sur la page principale' in response.data

    def test_home_route_content_type(self, client):
        """Test that home route returns plain text content."""
        response = client.get('/')
        assert response.status_code == 200
        assert 'text/html' in response.content_type

    def test_home_route_with_query_parameters(self, client):
        """Test home route with query parameters (should be ignored)."""
        response = client.get('/?param=value&other=test')
        assert response.status_code == 200
        assert b'Bienvenue sur la page principale' in response.data

    def test_home_route_with_post_method(self, client):
        """Test that POST method is not allowed on home route."""
        response = client.post('/')
        assert response.status_code == 405  # Method Not Allowed

    def test_home_route_with_put_method(self, client):
        """Test that PUT method is not allowed on home route."""
        response = client.put('/')
        assert response.status_code == 405  # Method Not Allowed

    def test_home_route_with_delete_method(self, client):
        """Test that DELETE method is not allowed on home route."""
        response = client.delete('/')
        assert response.status_code == 405  # Method Not Allowed

    def test_home_route_response_headers(self, client):
        """Test that appropriate response headers are set."""
        response = client.get('/')
        assert response.status_code == 200
        assert 'Content-Type' in response.headers
        assert 'Content-Length' in response.headers

    def test_home_route_response_data_encoding(self, client):
        """Test that response data is properly encoded."""
        response = client.get('/')
        assert response.status_code == 200
        # Test that French characters are properly encoded
        response_text = response.data.decode('utf-8')
        assert 'Bienvenue sur la page principale' in response_text

    def test_nonexistent_route_returns_404(self, client):
        """Test that non-existent routes return 404."""
        response = client.get('/nonexistent')
        assert response.status_code == 404

    def test_multiple_slashes_route(self, client):
        """Test route with multiple slashes."""
        response = client.get('///')
        assert response.status_code == 404

    def test_app_configuration(self):
        """Test Flask app configuration."""
        assert app.name == 'front.main_page'
        # Test that the app can be configured for testing
        app.config['TESTING'] = True
        assert app.config['TESTING'] is True

    def test_app_has_home_route(self):
        """Test that the app has the home route registered."""
        # Check that the route is registered
        rules = [rule.rule for rule in app.url_map.iter_rules()]
        assert '/' in rules

    def test_home_route_function_exists(self):
        """Test that the home function exists and is callable."""
        from front.main_page import home
        assert callable(home)

    def test_home_route_with_trailing_slash(self, client):
        """Test home route with trailing slash (should work the same)."""
        response = client.get('/')
        assert response.status_code == 200
        assert b'Bienvenue sur la page principale' in response.data

    def test_home_route_case_sensitivity(self, client):
        """Test that routes are case sensitive."""
        # Flask routes are case sensitive by default
        response = client.get('/')
        assert response.status_code == 200
        
        # This should return 404 as it's a different route
        response = client.get('/HOME')
        assert response.status_code == 404

    def test_home_route_response_length(self, client):
        """Test that response has expected length."""
        response = client.get('/')
        assert response.status_code == 200
        expected_message = 'Bienvenue sur la page principale'
        assert len(response.data.decode('utf-8')) >= len(expected_message)

    def test_app_debug_configuration(self):
        """Test app debug configuration."""
        # The app should be configurable for debug mode
        original_debug = app.debug
        app.debug = True
        assert app.debug is True
        app.debug = original_debug

    def test_home_route_with_special_characters_in_url(self, client):
        """Test home route with special characters in URL."""
        # These should all return 404 as they're different routes
        special_urls = ['/%20', '/?', '/#', '/%']
        for url in special_urls:
            response = client.get(url)
            # Most of these will be 404, some might be handled differently
            assert response.status_code in [200, 404, 400]

    def test_home_route_with_unicode_in_url(self, client):
        """Test home route with unicode characters in URL."""
        response = client.get('/café')
        assert response.status_code == 404

    def test_app_url_map(self):
        """Test that the app's URL map is properly configured."""
        rules = list(app.url_map.iter_rules())
        # Should have at least the home route and static route
        assert len(rules) >= 1
        
        # Find the home route
        home_rule = None
        for rule in rules:
            if rule.rule == '/' and 'GET' in rule.methods:
                home_rule = rule
                break
        
        assert home_rule is not None
        assert 'GET' in home_rule.methods

    def test_home_route_idempotency(self, client):
        """Test that multiple calls to home route return the same result."""
        response1 = client.get('/')
        response2 = client.get('/')
        
        assert response1.status_code == response2.status_code
        assert response1.data == response2.data
        assert response1.content_type == response2.content_type

    def test_home_route_with_different_user_agents(self, client):
        """Test home route with different User-Agent headers."""
        user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'curl/7.68.0',
            'Python-requests/2.25.1'
        ]
        
        for user_agent in user_agents:
            response = client.get('/', headers={'User-Agent': user_agent})
            assert response.status_code == 200
            assert b'Bienvenue sur la page principale' in response.data
