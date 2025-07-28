import unittest
import tempfile
import os
import shutil
from unittest.mock import patch
from create_static_files import (
    get_robots_txt_content,
    get_sitemap_xml_content,
    find_streamlit_static_root,
    create_static_files,
    BASE_URL,
    current_date
)


class TestStaticFileContent(unittest.TestCase):

    @patch('create_static_files.BASE_URL', 'https://custom.example.com')
    def test_get_robots_txt_content_custom_base_url(self):
        """Test robots.txt content generation with custom BASE_URL"""
        content = get_robots_txt_content()
        self.assertIn("User-agent: *", content)
        self.assertIn("Allow: /", content)
        self.assertIn("Sitemap: https://custom.example.com/sitemap.xml", content)

    def test_get_robots_txt_content(self):
        """Test robots.txt content generation"""
        content = get_robots_txt_content()
        self.assertIn("User-agent: *", content)
        self.assertIn("Allow: /", content)
        self.assertIn(f"Sitemap: {BASE_URL}/sitemap.xml", content)

    def test_get_sitemap_xml_content(self):
        """Test sitemap.xml content generation"""
        content = get_sitemap_xml_content()
        self.assertIn('<?xml version="1.0" encoding="UTF-8"?>', content)
        self.assertIn('<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">', content)
        self.assertIn(f'<loc>{BASE_URL}/</loc>', content)
        self.assertIn(f'<loc>{BASE_URL}/?lang=ja</loc>', content)
        self.assertIn(f'<loc>{BASE_URL}/?lang=en</loc>', content)
        self.assertIn(f'<loc>{BASE_URL}/?lang=ko</loc>', content)
        self.assertIn(f'<loc>{BASE_URL}/?lang=zh-cn</loc>', content)
        self.assertIn(f'<loc>{BASE_URL}/?lang=zh-tw</loc>', content)
        self.assertIn(f'<loc>{BASE_URL}/?lang=th</loc>', content)
        self.assertIn(f'<loc>{BASE_URL}/?lang=vi</loc>', content)
        self.assertIn(f'<loc>{BASE_URL}/?lang=id</loc>', content)
        self.assertIn(f'<loc>{BASE_URL}/?lang=hi</loc>', content)
        self.assertIn(f'<lastmod>{current_date}</lastmod>', content)

    @patch('create_static_files.BASE_URL', 'https://test.example.com')
    @patch('create_static_files.current_date', '2025-12-25')
    def test_get_sitemap_xml_content_custom_config(self):
        """Test sitemap.xml content generation with custom configuration"""
        content = get_sitemap_xml_content()
        self.assertIn('<?xml version="1.0" encoding="UTF-8"?>', content)
        self.assertIn('<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">', content)
        self.assertIn('<loc>https://test.example.com/</loc>', content)
        self.assertIn('<loc>https://test.example.com/?lang=ja</loc>', content)
        self.assertIn('<lastmod>2025-12-25</lastmod>', content)


class TestFindStreamlitStaticRoot(unittest.TestCase):

    @patch('os.path.exists')
    @patch('streamlit.__file__', '/usr/local/lib/python3.12/site-packages/streamlit/__init__.py')
    def test_find_via_package_introspection(self, mock_exists):
        """Test finding static directory via package introspection"""
        def side_effect(path):
            return path == "/usr/local/lib/python3.12/site-packages/streamlit/static"

        mock_exists.side_effect = side_effect

        result = find_streamlit_static_root()
        self.assertEqual(result, "/usr/local/lib/python3.12/site-packages/streamlit/static")

    @patch('os.path.exists')
    @patch('streamlit.__file__', '/usr/local/lib/python3.12/site-packages/streamlit/__init__.py')
    def test_find_via_fallback_paths(self, mock_exists):
        """Test finding static directory via fallback when package introspection fails"""
        def side_effect(path):
            # Package introspection path doesn't exist
            if path == "/usr/local/lib/python3.12/site-packages/streamlit/static":
                return False
            # But fallback path exists (different path)
            elif path == "/app/streamlit/frontend/build/static":
                return True
            return False

        mock_exists.side_effect = side_effect

        result = find_streamlit_static_root()
        self.assertEqual(result, "/app/streamlit/frontend/build/static")

    @patch('os.path.exists')
    def test_find_not_found(self, mock_exists):
        """Test when static directory is not found"""
        mock_exists.return_value = False

        result = find_streamlit_static_root()
        self.assertIsNone(result)


class TestCreateStaticFiles(unittest.TestCase):

    def setUp(self):
        """Setup temporary directory for tests"""
        self.temp_dir = tempfile.mkdtemp()

    def tearDown(self):
        """Cleanup temporary directory"""
        shutil.rmtree(self.temp_dir)

    def test_create_static_files_success(self):
        """Test successful creation of static files"""
        result = create_static_files(self.temp_dir)
        self.assertTrue(result)

        # Check robots.txt
        robots_path = os.path.join(self.temp_dir, "robots.txt")
        self.assertTrue(os.path.exists(robots_path))
        with open(robots_path, 'r', encoding='utf-8') as f:
            robots_content = f.read()
        self.assertIn("User-agent: *", robots_content)

        # Check sitemap.xml
        sitemap_path = os.path.join(self.temp_dir, "sitemap.xml")
        self.assertTrue(os.path.exists(sitemap_path))
        with open(sitemap_path, 'r', encoding='utf-8') as f:
            sitemap_content = f.read()
        self.assertIn('<?xml version="1.0" encoding="UTF-8"?>', sitemap_content)

    def test_create_static_files_nonexistent_directory(self):
        """Test creation fails with non-existent directory"""
        nonexistent_dir = os.path.join(self.temp_dir, "nonexistent")
        result = create_static_files(nonexistent_dir)
        self.assertFalse(result)

    @patch('create_static_files.find_streamlit_static_root')
    def test_create_static_files_auto_detect_success(self, mock_find):
        """Test auto-detection of static directory"""
        mock_find.return_value = self.temp_dir

        result = create_static_files()
        self.assertTrue(result)

        # Verify files were created
        self.assertTrue(os.path.exists(os.path.join(self.temp_dir, "robots.txt")))
        self.assertTrue(os.path.exists(os.path.join(self.temp_dir, "sitemap.xml")))

    @patch('create_static_files.find_streamlit_static_root')
    def test_create_static_files_auto_detect_failure(self, mock_find):
        """Test auto-detection failure"""
        mock_find.return_value = None

        result = create_static_files()
        self.assertFalse(result)

    @patch('builtins.open', side_effect=PermissionError("Permission denied"))
    def test_create_static_files_permission_error(self, mock_open):
        """Test handling of permission errors"""
        result = create_static_files(self.temp_dir)
        self.assertFalse(result)


if __name__ == '__main__':
    unittest.main()
