import pytest
from unittest.mock import patch, mock_open
import os
from front.gwsetup.path import BASE_DIR, safe_path, list_dir


class TestBaseDirConstant:
    """Tests for BASE_DIR constant."""

    def test_base_dir_value(self):
        """Test that BASE_DIR has the expected value."""
        assert BASE_DIR == '/host_files'

    def test_base_dir_is_string(self):
        """Test that BASE_DIR is a string."""
        assert isinstance(BASE_DIR, str)

    def test_base_dir_is_absolute_path(self):
        """Test that BASE_DIR is an absolute path."""
        assert os.path.isabs(BASE_DIR)


class TestSafePath:
    """Tests for safe_path function."""

    def test_safe_path_with_valid_relative_path(self):
        """Test safe_path with valid relative path."""
        result = safe_path('subdir/file.txt')
        expected = '/host_files/subdir/file.txt'
        assert result == expected

    def test_safe_path_with_empty_string(self):
        """Test safe_path with empty string."""
        result = safe_path('')
        expected = '/host_files'
        assert result == expected

    def test_safe_path_with_dot(self):
        """Test safe_path with current directory reference."""
        result = safe_path('.')
        expected = '/host_files'
        assert result == expected

    def test_safe_path_with_single_filename(self):
        """Test safe_path with single filename."""
        result = safe_path('file.txt')
        expected = '/host_files/file.txt'
        assert result == expected

    def test_safe_path_with_nested_directories(self):
        """Test safe_path with nested directories."""
        result = safe_path('dir1/dir2/dir3/file.txt')
        expected = '/host_files/dir1/dir2/dir3/file.txt'
        assert result == expected

    def test_safe_path_with_leading_slash(self):
        """Test safe_path with leading slash (should be treated as relative)."""
        result = safe_path('/subdir/file.txt')
        expected = '/host_files/subdir/file.txt'
        assert result == expected

    def test_safe_path_with_double_dots_blocked(self):
        """Test safe_path blocks directory traversal with double dots."""
        result = safe_path('../etc/passwd')
        expected = '/host_files'
        assert result == expected

    def test_safe_path_with_nested_double_dots_blocked(self):
        """Test safe_path blocks nested directory traversal."""
        result = safe_path('subdir/../../etc/passwd')
        expected = '/host_files'
        assert result == expected

    def test_safe_path_with_multiple_double_dots_blocked(self):
        """Test safe_path blocks multiple directory traversal attempts."""
        result = safe_path('../../../../etc/passwd')
        expected = '/host_files'
        assert result == expected

    def test_safe_path_with_mixed_traversal_attempts(self):
        """Test safe_path blocks mixed directory traversal attempts."""
        result = safe_path('valid/../../invalid/../etc/passwd')
        expected = '/host_files'
        assert result == expected

    def test_safe_path_with_valid_path_containing_dots_in_filename(self):
        """Test safe_path allows dots in filenames."""
        result = safe_path('subdir/file.name.txt')
        expected = '/host_files/subdir/file.name.txt'
        assert result == expected

    def test_safe_path_with_special_characters(self):
        """Test safe_path with special characters in path."""
        result = safe_path('subdir/file-name_123.txt')
        expected = '/host_files/subdir/file-name_123.txt'
        assert result == expected

    def test_safe_path_with_spaces(self):
        """Test safe_path with spaces in path."""
        result = safe_path('sub dir/file name.txt')
        expected = '/host_files/sub dir/file name.txt'
        assert result == expected

    def test_safe_path_with_unicode_characters(self):
        """Test safe_path with unicode characters."""
        result = safe_path('dossier/fichier_été.txt')
        expected = '/host_files/dossier/fichier_été.txt'
        assert result == expected

    def test_safe_path_normalizes_path(self):
        """Test safe_path normalizes redundant path separators."""
        result = safe_path('subdir//file.txt')
        expected = '/host_files/subdir/file.txt'
        assert result == expected

    def test_safe_path_with_trailing_slash(self):
        """Test safe_path with trailing slash."""
        result = safe_path('subdir/')
        expected = '/host_files/subdir'
        assert result == expected

    def test_safe_path_with_none_input(self):
        """Test safe_path with None input."""
        result = safe_path(None)
        expected = '/host_files'
        assert result == expected

    def test_safe_path_with_absolute_path_outside_base(self):
        """Test safe_path with absolute path outside base directory."""
        result = safe_path('/etc/passwd')
        expected = '/host_files/etc/passwd'
        assert result == expected

    def test_safe_path_ensures_within_base_dir(self):
        """Test safe_path ensures result is within BASE_DIR."""
        test_paths = [
            'valid/path',
            '../invalid',
            '../../etc/passwd',
            'valid/../invalid',
            '/absolute/path'
        ]
        
        for path in test_paths:
            result = safe_path(path)
            assert result.startswith(BASE_DIR)


class TestListDir:
    """Tests for list_dir function."""

    @patch('os.path.exists')
    @patch('os.listdir')
    @patch('os.path.isdir')
    def test_list_dir_success(self, mock_isdir, mock_listdir, mock_exists):
        """Test list_dir with successful directory listing."""
        mock_exists.return_value = True
        mock_listdir.return_value = ['file1.txt', 'dir1', 'file2.py']
        mock_isdir.side_effect = lambda path: 'dir1' in path
        
        result = list_dir('test_dir')
        
        assert result['path'] == '/host_files/test_dir'
        assert result['parent'] == '/host_files'
        assert len(result['items']) == 3
        
        # Check items structure
        items_by_name = {item['name']: item for item in result['items']}
        
        assert 'file1.txt' in items_by_name
        assert items_by_name['file1.txt']['is_dir'] is False
        assert items_by_name['file1.txt']['path'] == '/host_files/test_dir/file1.txt'
        
        assert 'dir1' in items_by_name
        assert items_by_name['dir1']['is_dir'] is True
        assert items_by_name['dir1']['path'] == '/host_files/test_dir/dir1'
        
        assert 'file2.py' in items_by_name
        assert items_by_name['file2.py']['is_dir'] is False

    @patch('os.path.exists')
    def test_list_dir_nonexistent_directory(self, mock_exists):
        """Test list_dir with nonexistent directory."""
        mock_exists.return_value = False
        
        result = list_dir('nonexistent')
        
        assert result['path'] == '/host_files/nonexistent'
        assert result['parent'] == '/host_files'
        assert result['items'] == []

    @patch('os.path.exists')
    @patch('os.listdir')
    def test_list_dir_permission_error(self, mock_listdir, mock_exists):
        """Test list_dir with permission error."""
        mock_exists.return_value = True
        mock_listdir.side_effect = PermissionError('Permission denied')
        
        result = list_dir('restricted_dir')
        
        assert result['path'] == '/host_files/restricted_dir'
        assert result['parent'] == '/host_files'
        assert result['items'] == []

    @patch('os.path.exists')
    @patch('os.listdir')
    def test_list_dir_os_error(self, mock_listdir, mock_exists):
        """Test list_dir with OS error."""
        mock_exists.return_value = True
        mock_listdir.side_effect = OSError('OS error')
        
        result = list_dir('error_dir')
        
        assert result['path'] == '/host_files/error_dir'
        assert result['parent'] == '/host_files'
        assert result['items'] == []

    @patch('os.path.exists')
    @patch('os.listdir')
    @patch('os.path.isdir')
    def test_list_dir_empty_directory(self, mock_isdir, mock_listdir, mock_exists):
        """Test list_dir with empty directory."""
        mock_exists.return_value = True
        mock_listdir.return_value = []
        
        result = list_dir('empty_dir')
        
        assert result['path'] == '/host_files/empty_dir'
        assert result['parent'] == '/host_files'
        assert result['items'] == []

    @patch('os.path.exists')
    @patch('os.listdir')
    @patch('os.path.isdir')
    def test_list_dir_only_files(self, mock_isdir, mock_listdir, mock_exists):
        """Test list_dir with directory containing only files."""
        mock_exists.return_value = True
        mock_listdir.return_value = ['file1.txt', 'file2.py', 'file3.md']
        mock_isdir.return_value = False
        
        result = list_dir('files_only')
        
        assert len(result['items']) == 3
        for item in result['items']:
            assert item['is_dir'] is False
            assert item['name'] in ['file1.txt', 'file2.py', 'file3.md']

    @patch('os.path.exists')
    @patch('os.listdir')
    @patch('os.path.isdir')
    def test_list_dir_only_directories(self, mock_isdir, mock_listdir, mock_exists):
        """Test list_dir with directory containing only subdirectories."""
        mock_exists.return_value = True
        mock_listdir.return_value = ['dir1', 'dir2', 'dir3']
        mock_isdir.return_value = True
        
        result = list_dir('dirs_only')
        
        assert len(result['items']) == 3
        for item in result['items']:
            assert item['is_dir'] is True
            assert item['name'] in ['dir1', 'dir2', 'dir3']

    @patch('os.path.exists')
    @patch('os.listdir')
    @patch('os.path.isdir')
    def test_list_dir_with_hidden_files(self, mock_isdir, mock_listdir, mock_exists):
        """Test list_dir with hidden files (starting with dot)."""
        mock_exists.return_value = True
        mock_listdir.return_value = ['.hidden', '.config', 'visible.txt']
        mock_isdir.side_effect = lambda path: '.config' in path
        
        result = list_dir('with_hidden')
        
        assert len(result['items']) == 3
        items_by_name = {item['name']: item for item in result['items']}
        
        assert '.hidden' in items_by_name
        assert items_by_name['.hidden']['is_dir'] is False
        
        assert '.config' in items_by_name
        assert items_by_name['.config']['is_dir'] is True
        
        assert 'visible.txt' in items_by_name
        assert items_by_name['visible.txt']['is_dir'] is False

    @patch('os.path.exists')
    @patch('os.listdir')
    @patch('os.path.isdir')
    def test_list_dir_with_special_characters(self, mock_isdir, mock_listdir, mock_exists):
        """Test list_dir with files containing special characters."""
        mock_exists.return_value = True
        mock_listdir.return_value = ['file with spaces.txt', 'file-with-dashes.py', 'file_with_underscores.md']
        mock_isdir.return_value = False
        
        result = list_dir('special_chars')
        
        assert len(result['items']) == 3
        names = [item['name'] for item in result['items']]
        assert 'file with spaces.txt' in names
        assert 'file-with-dashes.py' in names
        assert 'file_with_underscores.md' in names

    @patch('os.path.exists')
    @patch('os.listdir')
    @patch('os.path.isdir')
    def test_list_dir_with_unicode_filenames(self, mock_isdir, mock_listdir, mock_exists):
        """Test list_dir with unicode filenames."""
        mock_exists.return_value = True
        mock_listdir.return_value = ['fichier_été.txt', 'документ.doc', '文件.txt']
        mock_isdir.return_value = False
        
        result = list_dir('unicode_files')
        
        assert len(result['items']) == 3
        names = [item['name'] for item in result['items']]
        assert 'fichier_été.txt' in names
        assert 'документ.doc' in names
        assert '文件.txt' in names

    def test_list_dir_with_directory_traversal_attempt(self):
        """Test list_dir blocks directory traversal attempts."""
        result = list_dir('../etc')
        
        # Should be blocked by safe_path and default to BASE_DIR
        assert result['path'] == '/host_files'
        assert result['parent'] == '/host_files'

    def test_list_dir_with_absolute_path_outside_base(self):
        """Test list_dir with absolute path outside base directory."""
        result = list_dir('/etc/passwd')
        
        # Should be redirected to within BASE_DIR
        assert result['path'] == '/host_files/etc/passwd'
        assert result['parent'] == '/host_files/etc'

    @patch('os.path.exists')
    @patch('os.listdir')
    @patch('os.path.isdir')
    def test_list_dir_parent_calculation(self, mock_isdir, mock_listdir, mock_exists):
        """Test list_dir calculates parent directory correctly."""
        mock_exists.return_value = True
        mock_listdir.return_value = []
        
        # Test various directory levels
        test_cases = [
            ('', '/host_files', '/host_files'),
            ('subdir', '/host_files/subdir', '/host_files'),
            ('dir1/dir2', '/host_files/dir1/dir2', '/host_files/dir1'),
            ('dir1/dir2/dir3', '/host_files/dir1/dir2/dir3', '/host_files/dir1/dir2'),
        ]
        
        for input_path, expected_path, expected_parent in test_cases:
            result = list_dir(input_path)
            assert result['path'] == expected_path
            assert result['parent'] == expected_parent

    @patch('os.path.exists')
    @patch('os.listdir')
    @patch('os.path.isdir')
    def test_list_dir_isdir_exception_handling(self, mock_isdir, mock_listdir, mock_exists):
        """Test list_dir handles exceptions in isdir check."""
        mock_exists.return_value = True
        mock_listdir.return_value = ['file1.txt', 'problematic_item']
        mock_isdir.side_effect = lambda path: {
            '/host_files/test_dir/file1.txt': False,
            '/host_files/test_dir/problematic_item': OSError('Permission denied')
        }.get(path, False)
        
        result = list_dir('test_dir')
        
        # Should handle the exception gracefully and continue
        assert len(result['items']) == 2
        items_by_name = {item['name']: item for item in result['items']}
        
        assert 'file1.txt' in items_by_name
        assert items_by_name['file1.txt']['is_dir'] is False
        
        assert 'problematic_item' in items_by_name
        # Should default to False when isdir raises exception
        assert items_by_name['problematic_item']['is_dir'] is False

    def test_list_dir_return_structure(self):
        """Test list_dir returns correct structure."""
        with patch('os.path.exists', return_value=False):
            result = list_dir('test')
            
            # Check required keys
            assert 'path' in result
            assert 'parent' in result
            assert 'items' in result
            
            # Check types
            assert isinstance(result['path'], str)
            assert isinstance(result['parent'], str)
            assert isinstance(result['items'], list)

    @patch('os.path.exists')
    @patch('os.listdir')
    @patch('os.path.isdir')
    def test_list_dir_item_structure(self, mock_isdir, mock_listdir, mock_exists):
        """Test list_dir returns correct item structure."""
        mock_exists.return_value = True
        mock_listdir.return_value = ['test_item']
        mock_isdir.return_value = False
        
        result = list_dir('test')
        
        assert len(result['items']) == 1
        item = result['items'][0]
        
        # Check required keys in item
        assert 'name' in item
        assert 'is_dir' in item
        assert 'path' in item
        
        # Check types
        assert isinstance(item['name'], str)
        assert isinstance(item['is_dir'], bool)
        assert isinstance(item['path'], str)
        
        # Check values
        assert item['name'] == 'test_item'
        assert item['is_dir'] is False
        assert item['path'] == '/host_files/test/test_item'