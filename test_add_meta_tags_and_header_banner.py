import os
import unittest
from unittest import mock
import tempfile
import shutil
from bs4 import BeautifulSoup
import add_meta_tags_and_header_banner

possible_paths = [
    "/app/streamlit/frontend/build/index.html",
    "/usr/local/lib/python3.9/site-packages/streamlit/static/index.html",
    "/usr/local/lib/python3.8/dist-packages/streamlit/static/index.html",
    "/usr/local/lib/python3.12/site-packages/streamlit/static/index.html"
]


class TestAddMetaTagsAndHeaderBanner(unittest.TestCase):

    def setUp(self):
        """Setup before tests"""
        # Create temporary directory for testing
        self.test_dir = tempfile.mkdtemp()

        # Create test HTML file
        self.test_html = os.path.join(self.test_dir, 'test_index.html')
        with open(self.test_html, 'w') as f:
            f.write("""
            <!DOCTYPE html>
            <html>
            <head><title>Test Page</title></head>
            <body>Test Content</body>
            </html>
            """)

        self.custom_index_path = os.path.join(self.test_dir, 'custom_index.html')
        with open(self.custom_index_path, 'w') as f:
            f.write("""
            <!DOCTYPE html>
            <html>
            <head><title>Custom Page</title></head>
            <body>Custom Content</body>
            </html>
            """)

    def tearDown(self):
        """Cleanup after tests"""
        # Delete test directory
        shutil.rmtree(self.test_dir)

    def test_find_streamlit_index_path(self):
        """Test find_streamlit_index_path function - test both custom path and default paths"""

        # Test custom path - existing path
        custom_path = self.test_html
        self.assertEqual(add_meta_tags_and_header_banner.find_streamlit_index_path(custom_path), self.test_html)

        # Test custom path - non-existent path
        custom_path = "/non-existent/path/index.html"
        self.assertNotEqual(add_meta_tags_and_header_banner.find_streamlit_index_path(custom_path), custom_path)

        # Test when specific path exists
        for test_path in possible_paths:
            with mock.patch('os.path.exists', side_effect=lambda x: x == test_path):
                found_path = add_meta_tags_and_header_banner.find_streamlit_index_path()
                self.assertEqual(found_path, test_path)

    def test_create_backup(self):
        """Test create_backup function"""

        # Path to file for creating backup
        file_path = os.path.join(self.test_dir, 'test_index.html')
        add_meta_tags_and_header_banner.create_backup(file_path)
        self.assertTrue(os.path.exists(file_path + '.bak'))

    def test_get_meta_tags(self):
        """Test get_meta_tags function"""
        tags = add_meta_tags_and_header_banner.get_meta_tags()

        # Verify tags are a list
        self.assertIsInstance(tags, list)

        # Verify tags are dictionaries
        for tag in tags:
            self.assertIsInstance(tag, dict)

        # Verify required meta tags are included
        self.assertIn({'name': 'description', 'content': 'Azure Updates を要約して PPTX にまとめます。'}, tags)
        self.assertIn({'property': 'og:title', 'content': 'Azure Updates Summary'}, tags)

    def test_get_banner_style(self):
        """Test get_banner_style function"""

        style = add_meta_tags_and_header_banner.get_banner_style()

        # Verify style is a string
        self.assertIsInstance(style, str)

        # Verify required style elements are included
        self.assertIn('.header-banner', style)
        self.assertIn('position: fixed', style)

    def test_modify_html(self):
        """Test modify_html function"""

        # Test using custom path
        self.assertTrue(add_meta_tags_and_header_banner.modify_html(self.custom_index_path))

        # Check modified HTML
        with open(self.custom_index_path, 'r') as f:
            modified_html = f.read()

        soup = BeautifulSoup(modified_html, 'html.parser')

        # Verify meta tags have been added
        meta_tags = soup.find_all('meta')
        self.assertTrue(len(meta_tags) > 0)

        # Verify style tag has been added
        style_tag = soup.find('style')
        self.assertIsNotNone(style_tag)
        self.assertIn('.header-banner', style_tag.text)

        # Verify header banner has been added
        banner = soup.find('div', {'class': 'header-banner'})
        self.assertIsNotNone(banner)
        self.assertEqual(banner.text, "Public Preview")

        # Test with non-existent file
        non_existent_file_path = os.path.join(self.test_dir, 'non_existent.html')
        self.assertFalse(add_meta_tags_and_header_banner.modify_html(non_existent_file_path))


if __name__ == '__main__':
    unittest.main()
