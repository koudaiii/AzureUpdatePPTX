import unittest
import tempfile
import os
import shutil
from unittest.mock import patch, MagicMock
from create_static_files import (
    get_robots_txt_content,
    get_sitemap_xml_content,
    find_streamlit_static_root,
    create_static_files
)


class TestStaticFileContent(unittest.TestCase):

    def test_get_robots_txt_content(self):
        """Test robots.txt content generation"""
        content = get_robots_txt_content()
        self.assertIn("User-agent: *", content)
        self.assertIn("Allow: /", content)
        self.assertIn("Sitemap: https://azure.koudaiii.com/sitemap.xml", content)

    def test_get_sitemap_xml_content(self):
        """Test sitemap.xml content generation"""
        content = get_sitemap_xml_content()
        self.assertIn('<?xml version="1.0" encoding="UTF-8"?>', content)
        self.assertIn('<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">', content)
        self.assertIn('<loc>https://azure.koudaiii.com/</loc>', content)
        self.assertIn('<loc>https://azure.koudaiii.com/?lang=ja</loc>', content)
        self.assertIn('<loc>https://azure.koudaiii.com/?lang=en</loc>', content)
        self.assertIn('<loc>https://azure.koudaiii.com/?lang=ko</loc>', content)
        self.assertIn('<loc>https://azure.koudaiii.com/?lang=zh-cn</loc>', content)
        self.assertIn('<loc>https://azure.koudaiii.com/?lang=zh-tw</loc>', content)
        self.assertIn('<loc>https://azure.koudaiii.com/?lang=th</loc>', content)
        self.assertIn('<loc>https://azure.koudaiii.com/?lang=vi</loc>', content)
        self.assertIn('<loc>https://azure.koudaiii.com/?lang=id</loc>', content)
        self.assertIn('<loc>https://azure.koudaiii.com/?lang=hi</loc>', content)


class TestFindStreamlitStaticRoot(unittest.TestCase):

    @patch('os.path.exists')
    def test_find_via_index_html(self, mock_exists):
        """Test finding static directory via index.html"""
        def side_effect(path):
            return path == "/usr/local/lib/python3.12/site-packages/streamlit/static/index.html"
        
        mock_exists.side_effect = side_effect
        
        result = find_streamlit_static_root()
        self.assertEqual(result, "/usr/local/lib/python3.12/site-packages/streamlit/static")

    @patch('os.path.exists')
    def test_find_via_static_directory(self, mock_exists):
        """Test finding static directory directly"""
        def side_effect(path):
            return path == "/usr/local/lib/python3.12/site-packages/streamlit/static"
        
        mock_exists.side_effect = side_effect
        
        result = find_streamlit_static_root()
        self.assertEqual(result, "/usr/local/lib/python3.12/site-packages/streamlit/static")

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