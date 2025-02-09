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


class TestGetArticle(unittest.TestCase):
    @patch('azureupdatehelper.requests.get')
    def test_get_article_calls_api(self, mock_get):
        mock_response = MagicMock()
        mock_response.text = '{"title":"Fake Title"}'
        mock_response.json.return_value = {"title": "Fake Title"}
        mock_response.status_code = 200
        mock_get.return_value = mock_response

        url = "https://fake.url/path?id=12345"
        response = azureupdatehelper.get_article(url)
        mock_get.assert_called_once()
        self.assertIsNotNone(response)
        self.assertEqual(response.json()['title'], "Fake Title")

    def test_get_article_calls_api_empty_id(self):
        url = "https://fake.url/path?id="
        response = azureupdatehelper.get_article(url)
        self.assertIsNone(response)

    def test_get_article_calls_api_no_id(self):
        url = "https://fake.url/path"
        response = azureupdatehelper.get_article(url)
        self.assertIsNone(response)

    def test_get_article_calls_api_faildocid(self):
        url = "https://fake.url/path?id=faildocid"
        response = azureupdatehelper.get_article(url)
        self.assertIsNone(response)


class TestAzureOpenAIClient(unittest.TestCase):
    @patch('azureupdatehelper.logging.debug')
    def test_azure_openai_client(self, mock_debug):
        client, deployment_name = azureupdatehelper.azure_openai_client(
            "fake_key",
            "https://example.com/deployments/test/?api-version=2024-08-01-preview"
        )
        self.assertEqual(client.api_key, "fake_key")
        self.assertEqual(deployment_name, "test")
        self.assertEqual(client._api_version, "2024-08-01-preview")

    def test_azure_openai_client_empty_param(self):
        client, deployment_name = azureupdatehelper.azure_openai_client(
            "fake_key",
            "https://example.com/deployments/test/"
        )
        self.assertIsNone(client)
        self.assertIsNone(deployment_name)

    def test_azure_openai_client_no_api_version_param(self):
        client, deployment_name = azureupdatehelper.azure_openai_client(
            "fake_key",
            "https://example.com/deployments/test/?api-versions="
        )
        self.assertIsNone(client)
        self.assertIsNone(deployment_name)

    def test_azure_openai_client_no_api_version(self):
        client, deployment_name = azureupdatehelper.azure_openai_client(
            "fake_key",
            "https://example.com/deployments/test/?api-version="
        )
        self.assertIsNone(client)
        self.assertIsNone(deployment_name)

    def test_azure_openai_client_no_deployment(self):
        client, deployment_name = azureupdatehelper.azure_openai_client(
            "fake_key",
            "https://example.com/test/?api-version=2024-08-01-preview"
        )
        self.assertIsNone(client)
        self.assertIsNone(deployment_name)


class TestSummarizeArticle(unittest.TestCase):
    def test_summarize_article_returns_summary(self):
        mock_client = MagicMock()
        mock_deployment_name = "Fake Deployment"
        mock_chat_completions = MagicMock()
        mock_chat_completions.create.return_value.choices = [
            MagicMock(message=MagicMock(content="Fake Summary"))
        ]
        mock_client.chat.completions = mock_chat_completions
        article = {
            "title": "Dummy article content",
            "products": ["Azure"],
            "description": "<p>Some description with <a href='https://example.com'>link</a></p>"
        }
        summary = azureupdatehelper.summarize_article(mock_client, mock_deployment_name, article)
        self.assertEqual(summary, ('Fake Summary', 'https://example.com'))

        content = 'タイトル: Dummy article content\n製品: Azure\n説明: Some description with link\n説明内のリンク: https://example.com'
        mock_chat_completions.create.assert_called_once_with(
            model=mock_deployment_name,
            messages=[
                {"role": "system", "content": azureupdatehelper.systemprompt},
                {"role": "user", "content": content}
            ]
        )


class TestTargetUrl(unittest.TestCase):
    def test_target_url_valid_id(self):
        self.assertEqual(
            "https://www.microsoft.com/releasecommunications/api/v2/azure/testid",
            azureupdatehelper.target_url("testid")
        )

    def test_target_url_empty_id(self):
        self.assertIsNone(azureupdatehelper.target_url(""))

    def test_target_url_none_id(self):
        self.assertIsNone(azureupdatehelper.target_url(None))


class TestDocidFromUrl(unittest.TestCase):
    def test_docid_from_url_valid_id(self):
        url = 'https://fake.url/path?id=test_doc_id'
        docid = azureupdatehelper.docid_from_url(url)
        self.assertEqual(docid, 'test_doc_id')

    def test_docid_from_url_empty_id(self):
        url = 'https://fake.url/path?id='
        docid = azureupdatehelper.docid_from_url(url)
        self.assertIsNone(docid)

    def test_docid_from_url_no_id(self):
        url = 'https://fake.url/path?foo=1'
        docid = azureupdatehelper.docid_from_url(url)
        self.assertIsNone(docid)

    def test_docid_from_url_no_query(self):
        url = 'https://fake.url/path'
        docid = azureupdatehelper.docid_from_url(url)
        self.assertIsNone(docid)


class TestRemoveHtmlTags(unittest.TestCase):
    def test_remove_html_tags_no_tags(self):
        text = "Just some text."
        self.assertEqual(azureupdatehelper.remove_html_tags(text), text)

    def test_remove_html_tags_with_simple_tags(self):
        text = "<b>Bold</b> text with <i>italic</i> tags."
        expected = "Bold text with italic tags."
        self.assertEqual(azureupdatehelper.remove_html_tags(text), expected)

    def test_remove_html_tags_nested_tags(self):
        text = "<div><p>Paragraph with <span>nested</span> tag</p></div>"
        expected = "Paragraph with nested tag"
        self.assertEqual(azureupdatehelper.remove_html_tags(text), expected)

    def test_remove_html_tags_empty_string(self):
        text = ""
        self.assertEqual(azureupdatehelper.remove_html_tags(text), "")


class TestGetAHrefFromHtml(unittest.TestCase):
    def test_get_a_href_from_html_no_links(self):
        html_content = "No anchor tags here."
        links = azureupdatehelper.get_a_href_from_html(html_content)
        self.assertEqual(links, [], "Expected empty list when no <a> tags present.")

    def test_get_a_href_from_html_single_link(self):
        html_content = '<p>Click <a href="https://example.com">here</a> to visit.</p>'
        links = azureupdatehelper.get_a_href_from_html(html_content)
        self.assertEqual(len(links), 1, "Expected one link in the list.")
        self.assertEqual(links[0], "https://example.com")

    def test_get_a_href_from_html_single_link_and_single_quote(self):
        html_content = "<p>Click <a href='https://example.com'>here</a> to visit.</p>"
        links = azureupdatehelper.get_a_href_from_html(html_content)
        self.assertEqual(len(links), 1, "Expected one link in the list.")
        self.assertEqual(links[0], "https://example.com")

    def test_get_a_href_from_html_single_link_and_no_quote(self):
        html_content = '<p>Click <a href=https://example.com>here</a> to visit.</p>'
        links = azureupdatehelper.get_a_href_from_html(html_content)
        self.assertEqual(len(links), 1, "Expected one link in the list.")
        self.assertEqual(links[0], "https://example.com")

    def test_get_a_href_from_html_multiple_links(self):
        html_content = '''
            <div>
                <a href="https://example.com/page1">Link1</a>
                <a href='https://example.com/page2'>Link2</a>
                <a href=https://example.com/page3>Link3</a>
            </div>
        '''
        links = azureupdatehelper.get_a_href_from_html(html_content)
        self.assertEqual(len(links), 3)
        self.assertIn("https://example.com/page1", links)
        self.assertIn("https://example.com/page2", links)
        self.assertIn("https://example.com/page3", links)

    def test_get_a_href_from_html_empty_string(self):
        links = azureupdatehelper.get_a_href_from_html("")
        self.assertEqual(links, [], "Expected empty list for empty HTML string.")


if __name__ == '__main__':
    unittest.main()
