import unittest
from unittest.mock import patch, MagicMock
import azureupdatehelper
import os
from datetime import datetime


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


class TestGetUpdateUrls(unittest.TestCase):
    @patch('azureupdatehelper.get_rss_feed_entries')
    @patch('azureupdatehelper.datetime')
    def test_get_update_urls_within_days(self, mock_datetime, mock_get_rss_feed_entries):
        mock_datetime.now.return_value = datetime(2024, 11, 7)
        mock_datetime.side_effect = lambda *args, **kw: datetime(*args, **kw)

        mock_entry = MagicMock()
        mock_entry.published = 'Sat, 2 Nov 2024 21:45:07 Z'
        mock_entry.link = 'https://example.com/update1'
        mock_get_rss_feed_entries.return_value = [mock_entry]

        mock_datetime.strptime().astimezone.return_value = datetime.strptime(
            mock_entry.published, azureupdatehelper.DATE_FORMAT
        ).astimezone()

        urls = azureupdatehelper.get_update_urls(7)
        self.assertEqual(len(urls), 1)
        self.assertEqual(urls[0], 'https://example.com/update1')

    @patch('azureupdatehelper.get_rss_feed_entries')
    @patch('azureupdatehelper.datetime')
    def test_get_update_urls_outside_days(self, mock_datetime, mock_get_rss_feed_entries):
        mock_datetime.now.return_value = datetime(2024, 11, 7)
        mock_datetime.side_effect = lambda *args, **kw: datetime(*args, **kw)

        mock_entry = MagicMock()
        mock_entry.published = 'Sat, 2 Nov 2024 21:45:07 Z'
        mock_entry.link = 'https://example.com/update1'
        mock_get_rss_feed_entries.return_value = [mock_entry]

        mock_datetime.strptime().astimezone.return_value = datetime.strptime(
            mock_entry.published, azureupdatehelper.DATE_FORMAT
        ).astimezone()

        urls = azureupdatehelper.get_update_urls(1)
        self.assertEqual(len(urls), 0)

    @patch('azureupdatehelper.get_rss_feed_entries')
    @patch('azureupdatehelper.datetime')
    def test_get_update_urls_no_published_date(self, mock_datetime, mock_get_rss_feed_entries):
        mock_datetime.now.return_value = datetime(2024, 11, 7)
        mock_datetime.side_effect = lambda *args, **kw: datetime(*args, **kw)

        mock_entry = MagicMock()
        mock_entry.published = None
        mock_entry.link = None
        mock_get_rss_feed_entries.return_value = [mock_entry]

        mock_datetime.strptime().astimezone.return_value = None

        urls = azureupdatehelper.get_update_urls(7)
        self.assertEqual(len(urls), 0)


if __name__ == '__main__':
    unittest.main()
