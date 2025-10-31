import pytest
from unittest.mock import patch
from front.start.start_app import app


class TestStartApp:
    """Tests for start Flask application."""

    @pytest.fixture
    def client(self):
        """Create a test client for the Flask app."""
        app.config['TESTING'] = True
        with app.test_client() as client:
            yield client

    def test_home_route_default_language(self, client):
        """Test home route with default language (no Accept-Language header)."""
        with patch('front.start.start_app.render_template') as mock_render:
            mock_render.return_value = 'rendered_template'
            response = client.get('/')
            
            assert response.status_code == 200
            mock_render.assert_called_once_with('geneweb.html', lang='en')

    def test_home_route_with_english_accept_language(self, client):
        """Test home route with English Accept-Language header."""
        with patch('front.start.start_app.render_template') as mock_render:
            mock_render.return_value = 'rendered_template'
            headers = {'Accept-Language': 'en-US,en;q=0.9'}
            response = client.get('/', headers=headers)
            
            assert response.status_code == 200
            mock_render.assert_called_once_with('geneweb.html', lang='en')

    def test_home_route_with_french_accept_language(self, client):
        """Test home route with French Accept-Language header."""
        with patch('front.start.start_app.render_template') as mock_render:
            mock_render.return_value = 'rendered_template'
            headers = {'Accept-Language': 'fr-FR,fr;q=0.9,en;q=0.8'}
            response = client.get('/', headers=headers)
            
            assert response.status_code == 200
            mock_render.assert_called_once_with('geneweb.html', lang='fr')

    def test_home_route_with_german_accept_language(self, client):
        """Test home route with German Accept-Language header."""
        with patch('front.start.start_app.render_template') as mock_render:
            mock_render.return_value = 'rendered_template'
            headers = {'Accept-Language': 'de-DE,de;q=0.9'}
            response = client.get('/', headers=headers)
            
            assert response.status_code == 200
            mock_render.assert_called_once_with('geneweb.html', lang='de')

    def test_home_route_with_spanish_accept_language(self, client):
        """Test home route with Spanish Accept-Language header."""
        with patch('front.start.start_app.render_template') as mock_render:
            mock_render.return_value = 'rendered_template'
            headers = {'Accept-Language': 'es-ES,es;q=0.9'}
            response = client.get('/', headers=headers)
            
            assert response.status_code == 200
            mock_render.assert_called_once_with('geneweb.html', lang='es')

    def test_home_route_with_italian_accept_language(self, client):
        """Test home route with Italian Accept-Language header."""
        with patch('front.start.start_app.render_template') as mock_render:
            mock_render.return_value = 'rendered_template'
            headers = {'Accept-Language': 'it-IT,it;q=0.9'}
            response = client.get('/', headers=headers)
            
            assert response.status_code == 200
            mock_render.assert_called_once_with('geneweb.html', lang='it')

    def test_home_route_with_portuguese_accept_language(self, client):
        """Test home route with Portuguese Accept-Language header."""
        with patch('front.start.start_app.render_template') as mock_render:
            mock_render.return_value = 'rendered_template'
            headers = {'Accept-Language': 'pt-BR,pt;q=0.9'}
            response = client.get('/', headers=headers)
            
            assert response.status_code == 200
            mock_render.assert_called_once_with('geneweb.html', lang='pt')

    def test_home_route_with_dutch_accept_language(self, client):
        """Test home route with Dutch Accept-Language header."""
        with patch('front.start.start_app.render_template') as mock_render:
            mock_render.return_value = 'rendered_template'
            headers = {'Accept-Language': 'nl-NL,nl;q=0.9'}
            response = client.get('/', headers=headers)
            
            assert response.status_code == 200
            mock_render.assert_called_once_with('geneweb.html', lang='nl')

    def test_home_route_with_unsupported_language_defaults_to_english(self, client):
        """Test home route with unsupported language defaults to English."""
        with patch('front.start.start_app.render_template') as mock_render:
            mock_render.return_value = 'rendered_template'
            headers = {'Accept-Language': 'ja-JP,ja;q=0.9'}
            response = client.get('/', headers=headers)
            
            assert response.status_code == 200
            mock_render.assert_called_once_with('geneweb.html', lang='en')

    def test_home_route_with_multiple_languages_chooses_best_match(self, client):
        """Test home route with multiple languages chooses best match."""
        with patch('front.start.start_app.render_template') as mock_render:
            mock_render.return_value = 'rendered_template'
            headers = {'Accept-Language': 'ja;q=0.9,fr;q=0.8,en;q=0.7'}
            response = client.get('/', headers=headers)
            
            assert response.status_code == 200
            # Should choose French as it's supported and has higher priority than English
            mock_render.assert_called_once_with('geneweb.html', lang='fr')

    def test_home_route_with_malformed_accept_language(self, client):
        """Test home route with malformed Accept-Language header."""
        with patch('front.start.start_app.render_template') as mock_render:
            mock_render.return_value = 'rendered_template'
            headers = {'Accept-Language': 'invalid-header-format'}
            response = client.get('/', headers=headers)
            
            assert response.status_code == 200
            # Should default to English when header is malformed
            mock_render.assert_called_once_with('geneweb.html', lang='en')

    def test_home_route_with_empty_accept_language(self, client):
        """Test home route with empty Accept-Language header."""
        with patch('front.start.start_app.render_template') as mock_render:
            mock_render.return_value = 'rendered_template'
            headers = {'Accept-Language': ''}
            response = client.get('/', headers=headers)
            
            assert response.status_code == 200
            mock_render.assert_called_once_with('geneweb.html', lang='en')

    def test_home_route_with_wildcard_accept_language(self, client):
        """Test home route with wildcard Accept-Language header."""
        with patch('front.start.start_app.render_template') as mock_render:
            mock_render.return_value = 'rendered_template'
            headers = {'Accept-Language': '*'}
            response = client.get('/', headers=headers)
            
            assert response.status_code == 200
            mock_render.assert_called_once_with('geneweb.html', lang='en')

    def test_home_route_with_case_insensitive_language(self, client):
        """Test home route with case insensitive language codes."""
        with patch('front.start.start_app.render_template') as mock_render:
            mock_render.return_value = 'rendered_template'
            headers = {'Accept-Language': 'FR-fr,FR;q=0.9'}
            response = client.get('/', headers=headers)
            
            assert response.status_code == 200
            mock_render.assert_called_once_with('geneweb.html', lang='fr')

    def test_404_error_handler_with_english(self, client):
        """Test 404 error handler with English language."""
        with patch('front.start.start_app.render_template') as mock_render:
            mock_render.return_value = 'rendered_404_template'
            headers = {'Accept-Language': 'en-US,en;q=0.9'}
            response = client.get('/nonexistent', headers=headers)
            
            assert response.status_code == 404
            mock_render.assert_called_once_with('404.html', lang='en', path='/nonexistent')

    def test_404_error_handler_with_french(self, client):
        """Test 404 error handler with French language."""
        with patch('front.start.start_app.render_template') as mock_render:
            mock_render.return_value = 'rendered_404_template'
            headers = {'Accept-Language': 'fr-FR,fr;q=0.9'}
            response = client.get('/page-inexistante', headers=headers)
            
            assert response.status_code == 404
            mock_render.assert_called_once_with('404.html', lang='fr', path='/page-inexistante')

    def test_404_error_handler_with_unsupported_language(self, client):
        """Test 404 error handler with unsupported language defaults to English."""
        with patch('front.start.start_app.render_template') as mock_render:
            mock_render.return_value = 'rendered_404_template'
            headers = {'Accept-Language': 'ja-JP,ja;q=0.9'}
            response = client.get('/存在しないページ', headers=headers)
            
            assert response.status_code == 404
            mock_render.assert_called_once_with('404.html', lang='en', path='/存在しないページ')

    def test_404_error_handler_no_accept_language(self, client):
        """Test 404 error handler without Accept-Language header."""
        with patch('front.start.start_app.render_template') as mock_render:
            mock_render.return_value = 'rendered_404_template'
            response = client.get('/missing')
            
            assert response.status_code == 404
            mock_render.assert_called_once_with('404.html', lang='en', path='/missing')

    def test_home_route_with_post_method_not_allowed(self, client):
        """Test that POST method is not allowed on home route."""
        response = client.post('/')
        assert response.status_code == 405  # Method Not Allowed

    def test_home_route_with_put_method_not_allowed(self, client):
        """Test that PUT method is not allowed on home route."""
        response = client.put('/')
        assert response.status_code == 405  # Method Not Allowed

    def test_home_route_with_delete_method_not_allowed(self, client):
        """Test that DELETE method is not allowed on home route."""
        response = client.delete('/')
        assert response.status_code == 405  # Method Not Allowed

    def test_home_route_with_query_parameters(self, client):
        """Test home route with query parameters (should be ignored)."""
        with patch('front.start.start_app.render_template') as mock_render:
            mock_render.return_value = 'rendered_template'
            response = client.get('/?param=value&other=test')
            
            assert response.status_code == 200
            mock_render.assert_called_once_with('geneweb.html', lang='en')

    def test_home_route_response_headers(self, client):
        """Test that appropriate response headers are set."""
        response = client.get('/')
        assert response.status_code == 200
        assert 'Content-Type' in response.headers
        assert 'Content-Length' in response.headers

    def test_home_route_idempotency(self, client):
        """Test that multiple calls to home route return consistent results."""
        headers = {'Accept-Language': 'fr-FR,fr;q=0.9'}
        
        with patch('front.start.start_app.render_template') as mock_render:
            mock_render.return_value = 'rendered_template'
            
            response1 = client.get('/', headers=headers)
            response2 = client.get('/', headers=headers)
            
            assert response1.status_code == response2.status_code
            assert mock_render.call_count == 2
            # Both calls should have the same arguments
            mock_render.assert_called_with('geneweb.html', lang='fr')

    def test_home_route_with_different_user_agents(self, client):
        """Test home route with different User-Agent headers."""
        user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'curl/7.68.0',
            'Python-requests/2.25.1'
        ]
        
        with patch('front.start.start_app.render_template') as mock_render:
            mock_render.return_value = 'rendered_template'
            
            for user_agent in user_agents:
                headers = {
                    'User-Agent': user_agent,
                    'Accept-Language': 'en-US,en;q=0.9'
                }
                response = client.get('/', headers=headers)
                assert response.status_code == 200

    def test_language_detection_with_complex_accept_language(self, client):
        """Test language detection with complex Accept-Language header."""
        test_cases = [
            ('en-US,en;q=0.9,fr;q=0.8,de;q=0.7', 'en'),
            ('fr-CA,fr;q=0.9,en;q=0.8', 'fr'),
            ('de-AT,de;q=0.9,en;q=0.8', 'de'),
            ('es-MX,es;q=0.9,en;q=0.8', 'es'),
            ('it-CH,it;q=0.9,fr;q=0.8,de;q=0.7', 'it'),
            ('pt-PT,pt;q=0.9,en;q=0.8', 'pt'),
            ('nl-BE,nl;q=0.9,fr;q=0.8', 'nl'),
            ('zh-CN,zh;q=0.9,en;q=0.8', 'en'),  # Unsupported, should default to en
        ]
        
        with patch('front.start.start_app.render_template') as mock_render:
            mock_render.return_value = 'rendered_template'
            
            for accept_lang, expected_lang in test_cases:
                headers = {'Accept-Language': accept_lang}
                response = client.get('/', headers=headers)
                
                assert response.status_code == 200
                mock_render.assert_called_with('geneweb.html', lang=expected_lang)
                mock_render.reset_mock()


class TestAppConfiguration:
    """Tests for Flask app configuration."""

    def test_app_name(self):
        """Test Flask app name."""
        assert app.name == 'front.start.start_app'

    def test_app_routes_registered(self):
        """Test that expected routes are registered."""
        rules = [rule.rule for rule in app.url_map.iter_rules()]
        assert '/' in rules

    def test_app_methods_allowed(self):
        """Test that correct HTTP methods are allowed for routes."""
        for rule in app.url_map.iter_rules():
            if rule.rule == '/':
                assert 'GET' in rule.methods
                assert 'POST' not in rule.methods

    def test_app_can_be_configured_for_testing(self):
        """Test that app can be configured for testing."""
        app.config['TESTING'] = True
        assert app.config['TESTING'] is True
        
        app.config['DEBUG'] = False
        assert app.config['DEBUG'] is False

    def test_app_has_error_handlers(self):
        """Test that app has error handlers registered."""
        # Check that 404 error handler is registered
        assert 404 in app.error_handler_spec[None]

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

    def test_app_supported_languages(self):
        """Test that the app supports expected languages."""
        # This is implicit from the language detection logic
        # The supported languages are: en, fr, de, es, it, pt, nl
        supported_languages = ['en', 'fr', 'de', 'es', 'it', 'pt', 'nl']
        
        # We can't directly test the supported languages list since it's not exposed,
        # but we can test that these languages are properly detected
        with app.test_client() as client:
            with patch('front.start.start_app.render_template') as mock_render:
                mock_render.return_value = 'rendered_template'
                
                for lang in supported_languages:
                    headers = {'Accept-Language': f'{lang}-XX,{lang};q=0.9'}
                    response = client.get('/', headers=headers)
                    
                    assert response.status_code == 200
                    mock_render.assert_called_with('geneweb.html', lang=lang)
                    mock_render.reset_mock()