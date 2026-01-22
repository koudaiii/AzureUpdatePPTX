import unittest
import azureupdatehelper


class TestAzureUpdatesAPIIntegration(unittest.TestCase):
    """Integration tests for Azure Updates API to verify urllib3/requests compatibility"""

    def test_rss_feed_retrieval(self):
        """Test retrieving RSS feed from Azure Updates API"""
        entries = azureupdatehelper.get_rss_feed_entries()

        self.assertIsNotNone(entries)
        self.assertIsInstance(entries, list)
        self.assertGreater(len(entries), 0, "RSS feed should contain at least one entry")

    def test_get_article_from_api(self):
        """Test retrieving an actual article from Azure Updates API"""
        entries = azureupdatehelper.get_rss_feed_entries()
        self.assertGreater(len(entries), 0, "Need at least one RSS entry")

        # Get the most recent article
        recent_url = entries[0].link
        response = azureupdatehelper.get_article(recent_url)

        self.assertIsNotNone(response)
        self.assertEqual(response.status_code, 200)

        # Verify response structure
        article_data = response.json()
        self.assertIn('title', article_data)
        self.assertIn('description', article_data)
        self.assertIn('products', article_data)


if __name__ == '__main__':
    unittest.main()
