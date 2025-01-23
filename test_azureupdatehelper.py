import unittest
from unittest.mock import patch, MagicMock
import azureupdatehelper
import os


class TestEnvironmentCheck(unittest.TestCase):
    @patch.dict(os.environ, {
        "API_KEY": "test_api_key",
        "API_ENDPOINT": "https://example.com/openai/deployments/gpt-4o/chat/completions?api-version=2024-08-01-preview"
    }, clear=True)
    def test_environment_check_all_set(self):
        self.assertTrue(azureupdatehelper.environment_check())

    @patch.dict(os.environ, {
        "API_KEY": "",
        "API_ENDPOINT": "https://example.com/openai/deployments/gpt-4o/chat/completions?api-version=2024-08-01-preview"
    }, clear=True)
    def test_environment_check_missing_api_key(self):
        self.assertFalse(azureupdatehelper.environment_check())

    @patch.dict(os.environ, {
        "API_KEY": "test_api_key",
        "API_ENDPOINT": ""
    }, clear=True)
    def test_environment_check_missing_api_endpoint(self):
        self.assertFalse(azureupdatehelper.environment_check())


class TestGetRssFeedEntries(unittest.TestCase):
    @patch('azureupdatehelper.feedparser.parse')
    def test_get_rss_feed_entries(self, mock_parse):
        mock_feed = MagicMock()
        mock_feed.entries = [{'id': '1', 'published': 'Thu, 31 Oct 2024 21:45:07 Z'}]
        mock_parse.return_value = mock_feed

        entries = azureupdatehelper.get_rss_feed_entries()
        self.assertEqual(len(entries), 1)
        self.assertEqual(entries[0]['id'], '1')


if __name__ == '__main__':
    unittest.main()
