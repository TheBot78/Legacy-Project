import pytest
from unittest.mock import patch, Mock, mock_open
from front.gwsetup.app import app, get_backend_candidates, get_db_stats, get_all_dbs, call_backend_delete, call_backend_rename


class TestGwsetupApp:
    """Tests for gwsetup Flask application."""

    @pytest.fixture
    def client(self):
        """Create a test client for the Flask app."""
        app.config['TESTING'] = True
        with app.test_client() as client:
            yield client

    def test_root_route_redirects_to_welcome(self, client):
        """Test that root route redirects to welcome."""
        response = client.get('/')
        assert response.status_code == 302
        assert '/welcome' in response.location

    def test_welcome_route_default_language(self, client):
        """Test welcome route with default language."""
        with patch('front.gwsetup.app.render_template') as mock_render:
            mock_render.return_value = 'rendered_template'
            response = client.get('/welcome')
            
            assert response.status_code == 200
            mock_render.assert_called_once_with('management_creation/welcome.html', lang='en')

    def test_welcome_route_with_language_parameter(self, client):
        """Test welcome route with language parameter."""
        with patch('front.gwsetup.app.render_template') as mock_render:
            mock_render.return_value = 'rendered_template'
            response = client.get('/welcome?lang=fr')
            
            assert response.status_code == 200
            mock_render.assert_called_once_with('management_creation/welcome.html', lang='fr')

    def test_welcome_route_invalid_language(self, client):
        """Test welcome route with invalid language (should default to en)."""
        with patch('front.gwsetup.app.render_template') as mock_render:
            mock_render.return_value = 'rendered_template'
            response = client.get('/welcome?lang=invalid')
            
            assert response.status_code == 200
            mock_render.assert_called_once_with('management_creation/welcome.html', lang='en')

    def test_ged2gwb_get_route(self, client):
        """Test ged2gwb GET route."""
        with patch('front.gwsetup.app.render_template') as mock_render:
            mock_render.return_value = 'rendered_template'
            response = client.get('/ged2gwb')
            
            assert response.status_code == 200
            mock_render.assert_called_once_with('management_creation/ged2gwb.html')

    @patch('builtins.open', new_callable=mock_open, read_data='GEDCOM file content')
    @patch('requests.post')
    def test_ged2gwb_post_route_success(self, mock_post, mock_file, client):
        """Test ged2gwb POST route with successful file upload."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {'status': 'success', 'db_name': 'test_db'}
        mock_post.return_value = mock_response
        
        data = {
            'file_path': '/path/to/test.ged',
            'db_name': 'test_db'
        }
        
        response = client.post('/ged2gwb', data=data)
        assert response.status_code == 302
        assert '/ged2gwb_result' in response.location

    def test_ged2gwb_post_route_missing_fields(self, client):
        """Test ged2gwb POST route with missing required fields."""
        with patch('front.gwsetup.app.render_template') as mock_render:
            mock_render.return_value = 'rendered_template'
            
            # Missing db_name
            response = client.post('/ged2gwb', data={'file_path': '/path/to/test.ged'})
            assert response.status_code == 200
            mock_render.assert_called_with('management_creation/ged2gwb.html', error='Missing required fields')

    @patch('builtins.open', side_effect=FileNotFoundError('File not found'))
    def test_ged2gwb_post_route_file_not_found(self, mock_file, client):
        """Test ged2gwb POST route with file not found error."""
        with patch('front.gwsetup.app.render_template') as mock_render:
            mock_render.return_value = 'rendered_template'
            
            data = {
                'file_path': '/nonexistent/file.ged',
                'db_name': 'test_db'
            }
            
            response = client.post('/ged2gwb', data=data)
            assert response.status_code == 200
            mock_render.assert_called_with('management_creation/ged2gwb.html', 
                                         error='Error reading file: File not found')

    @patch('front.gwsetup.app.get_db_stats')
    def test_ged2gwb_result_route(self, mock_get_db_stats, client):
        """Test ged2gwb_result route."""
        mock_get_db_stats.return_value = {'persons': 100, 'families': 50}
        
        with patch('front.gwsetup.app.render_template') as mock_render:
            mock_render.return_value = 'rendered_template'
            
            with client.session_transaction() as sess:
                sess['import_result'] = {'status': 'success', 'db_name': 'test_db'}
            
            response = client.get('/ged2gwb_result')
            assert response.status_code == 200
            mock_render.assert_called_once_with('management_creation/ged2gwb_result.html',
                                               result={'status': 'success', 'db_name': 'test_db'},
                                               db_stats={'persons': 100, 'families': 50})

    def test_gwc_get_route(self, client):
        """Test gwc GET route."""
        with patch('front.gwsetup.app.render_template') as mock_render:
            mock_render.return_value = 'rendered_template'
            response = client.get('/gwc')
            
            assert response.status_code == 200
            mock_render.assert_called_once_with('management_creation/gwc.html')

    @patch('builtins.open', new_callable=mock_open, read_data='GW file content')
    @patch('requests.post')
    def test_gwc_post_route_success(self, mock_post, mock_file, client):
        """Test gwc POST route with successful file upload."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {'status': 'success', 'db_name': 'test_db'}
        mock_post.return_value = mock_response
        
        data = {
            'file_path': '/path/to/test.gw',
            'db_name': 'test_db'
        }
        
        response = client.post('/gwc', data=data)
        assert response.status_code == 302
        assert '/gwc_result' in response.location

    def test_gwcempty_route(self, client):
        """Test gwcempty route."""
        with patch('front.gwsetup.app.render_template') as mock_render:
            mock_render.return_value = 'rendered_template'
            response = client.get('/gwcempty')
            
            assert response.status_code == 200
            mock_render.assert_called_once_with('management_creation/gwcempty.html')

    @patch('front.gwsetup.app.get_all_dbs')
    def test_rename_get_route(self, mock_get_all_dbs, client):
        """Test rename GET route."""
        mock_get_all_dbs.return_value = ['db1', 'db2', 'db3']
        
        with patch('front.gwsetup.app.render_template') as mock_render:
            mock_render.return_value = 'rendered_template'
            response = client.get('/rename')
            
            assert response.status_code == 200
            mock_render.assert_called_once_with('management_creation/rename.html', 
                                               databases=['db1', 'db2', 'db3'])

    @patch('front.gwsetup.app.call_backend_rename')
    def test_rename_post_route_success(self, mock_call_backend_rename, client):
        """Test rename POST route with successful rename."""
        mock_call_backend_rename.return_value = True
        
        data = {
            'old_name': 'old_db',
            'new_name': 'new_db'
        }
        
        response = client.post('/rename', data=data)
        assert response.status_code == 302
        mock_call_backend_rename.assert_called_once_with('old_db', 'new_db')

    @patch('front.gwsetup.app.get_all_dbs')
    def test_delete_get_route(self, mock_get_all_dbs, client):
        """Test delete GET route."""
        mock_get_all_dbs.return_value = ['db1', 'db2', 'db3']
        
        with patch('front.gwsetup.app.render_template') as mock_render:
            mock_render.return_value = 'rendered_template'
            response = client.get('/delete')
            
            assert response.status_code == 200
            mock_render.assert_called_once_with('management_creation/delete.html', 
                                               databases=['db1', 'db2', 'db3'])

    def test_delete_confirm_route(self, client):
        """Test delete_confirm route."""
        with patch('front.gwsetup.app.render_template') as mock_render:
            mock_render.return_value = 'rendered_template'
            
            data = {'selected_dbs': ['db1', 'db2']}
            response = client.post('/delete_confirm', data=data)
            
            assert response.status_code == 200
            mock_render.assert_called_once_with('management_creation/delete_confirm.html', 
                                               selected_dbs=['db1', 'db2'])

    @patch('front.gwsetup.app.call_backend_delete')
    def test_delete_result_route_success(self, mock_call_backend_delete, client):
        """Test delete_result route with successful deletion."""
        mock_call_backend_delete.return_value = True
        
        with patch('front.gwsetup.app.render_template') as mock_render:
            mock_render.return_value = 'rendered_template'
            
            data = {'confirmed_dbs': ['db1', 'db2']}
            response = client.post('/delete_result', data=data)
            
            assert response.status_code == 200
            # Should be called twice for each database
            assert mock_call_backend_delete.call_count == 2


class TestHelperFunctions:
    """Tests for helper functions in gwsetup app."""

    def test_get_backend_candidates(self):
        """Test get_backend_candidates returns expected URLs."""
        candidates = get_backend_candidates()
        expected_urls = [
            'http://127.0.0.1:8000',
            'http://localhost:8000',
            'http://host.docker.internal:8000'
        ]
        assert candidates == expected_urls

    @patch('requests.get')
    def test_get_db_stats_success(self, mock_get):
        """Test get_db_stats with successful response."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {'persons': 100, 'families': 50}
        mock_get.return_value = mock_response
        
        result = get_db_stats('test_db')
        assert result == {'persons': 100, 'families': 50}

    @patch('requests.get')
    def test_get_db_stats_failure(self, mock_get):
        """Test get_db_stats with failed response."""
        mock_get.side_effect = Exception('Connection error')
        
        result = get_db_stats('test_db')
        assert result == {}

    @patch('requests.get')
    def test_get_all_dbs_success(self, mock_get):
        """Test get_all_dbs with successful response."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = ['db1', 'db2', 'db3']
        mock_get.return_value = mock_response
        
        result = get_all_dbs()
        assert result == ['db1', 'db2', 'db3']

    @patch('requests.get')
    def test_get_all_dbs_failure(self, mock_get):
        """Test get_all_dbs with failed response."""
        mock_get.side_effect = Exception('Connection error')
        
        result = get_all_dbs()
        assert result == []

    @patch('requests.delete')
    def test_call_backend_delete_success(self, mock_delete):
        """Test call_backend_delete with successful response."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_delete.return_value = mock_response
        
        result = call_backend_delete('test_db')
        assert result is True

    @patch('requests.delete')
    def test_call_backend_delete_failure(self, mock_delete):
        """Test call_backend_delete with failed response."""
        mock_delete.side_effect = Exception('Connection error')
        
        result = call_backend_delete('test_db')
        assert result is False

    @patch('requests.put')
    def test_call_backend_rename_success(self, mock_put):
        """Test call_backend_rename with successful response."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_put.return_value = mock_response
        
        result = call_backend_rename('old_db', 'new_db')
        assert result is True

    @patch('requests.put')
    def test_call_backend_rename_failure(self, mock_put):
        """Test call_backend_rename with failed response."""
        mock_put.side_effect = Exception('Connection error')
        
        result = call_backend_rename('old_db', 'new_db')
        assert result is False

    @patch('requests.get')
    def test_helper_functions_try_multiple_backends(self, mock_get):
        """Test that helper functions try multiple backend URLs."""
        # First call fails, second succeeds
        mock_response_success = Mock()
        mock_response_success.status_code = 200
        mock_response_success.json.return_value = ['db1']
        
        mock_get.side_effect = [Exception('Connection error'), mock_response_success]
        
        result = get_all_dbs()
        assert result == ['db1']
        assert mock_get.call_count == 2

    @patch('requests.get')
    def test_get_db_stats_with_special_characters(self, mock_get):
        """Test get_db_stats with special characters in database name."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {'persons': 10}
        mock_get.return_value = mock_response
        
        result = get_db_stats('test-db_2023')
        assert result == {'persons': 10}
        mock_get.assert_called()

    @patch('requests.delete')
    def test_call_backend_delete_with_special_characters(self, mock_delete):
        """Test call_backend_delete with special characters in database name."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_delete.return_value = mock_response
        
        result = call_backend_delete('test-db_2023')
        assert result is True
        mock_delete.assert_called()

    @patch('requests.put')
    def test_call_backend_rename_with_special_characters(self, mock_put):
        """Test call_backend_rename with special characters in database names."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_put.return_value = mock_response
        
        result = call_backend_rename('old-db_2023', 'new-db_2024')
        assert result is True
        mock_put.assert_called()

    @patch('requests.get')
    def test_helper_functions_timeout_handling(self, mock_get):
        """Test helper functions handle timeouts properly."""
        import requests
        mock_get.side_effect = requests.Timeout('Request timeout')
        
        result = get_all_dbs()
        assert result == []
        
        result = get_db_stats('test_db')
        assert result == {}

    @patch('requests.get')
    def test_helper_functions_json_decode_error(self, mock_get):
        """Test helper functions handle JSON decode errors."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.side_effect = ValueError('Invalid JSON')
        mock_get.return_value = mock_response
        
        result = get_all_dbs()
        assert result == []
        
        result = get_db_stats('test_db')
        assert result == {}


class TestAppConfiguration:
    """Tests for Flask app configuration."""

    def test_app_name(self):
        """Test Flask app name."""
        assert app.name == 'front.gwsetup.app'

    def test_app_routes_registered(self):
        """Test that all expected routes are registered."""
        rules = [rule.rule for rule in app.url_map.iter_rules()]
        expected_routes = [
            '/', '/welcome', '/ged2gwb', '/ged2gwb_result',
            '/gwc', '/gwc_result', '/gwcempty', '/rename',
            '/delete', '/delete_confirm', '/delete_result'
        ]
        
        for route in expected_routes:
            assert route in rules

    def test_app_methods_allowed(self):
        """Test that correct HTTP methods are allowed for routes."""
        get_only_routes = ['/', '/welcome', '/ged2gwb_result', '/gwc_result', '/gwcempty']
        post_routes = ['/ged2gwb', '/gwc', '/rename', '/delete_confirm', '/delete_result']
        get_and_post_routes = ['/delete']
        
        for rule in app.url_map.iter_rules():
            if rule.rule in get_only_routes:
                assert 'GET' in rule.methods
                assert 'POST' not in rule.methods
            elif rule.rule in post_routes:
                assert 'POST' in rule.methods
            elif rule.rule in get_and_post_routes:
                assert 'GET' in rule.methods
                assert 'POST' in rule.methods

    def test_app_can_be_configured_for_testing(self):
        """Test that app can be configured for testing."""
        app.config['TESTING'] = True
        assert app.config['TESTING'] is True
        
        app.config['DEBUG'] = False
        assert app.config['DEBUG'] is False

    def test_app_secret_key_configuration(self):
        """Test that app can have secret key configured for sessions."""
        app.config['SECRET_KEY'] = 'test_secret_key'
        assert app.config['SECRET_KEY'] == 'test_secret_key'
