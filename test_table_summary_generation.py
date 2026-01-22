import unittest
from unittest.mock import MagicMock, patch
import azureupdatehelper as azup
from i18n_helper import I18nHelper, TABLE_SUMMARY_PROMPTS, LANGUAGES


class TestTableSummaryPrompts(unittest.TestCase):
    """Tests for TABLE_SUMMARY_PROMPTS dictionary"""

    def test_table_summary_prompts_exist_for_all_languages(self):
        """Test that TABLE_SUMMARY_PROMPTS has entries for all supported languages"""
        for lang_code in LANGUAGES.keys():
            self.assertIn(lang_code, TABLE_SUMMARY_PROMPTS,
                         f"TABLE_SUMMARY_PROMPTS missing entry for language: {lang_code}")

    def test_table_summary_prompts_are_not_empty(self):
        """Test that all TABLE_SUMMARY_PROMPTS entries are non-empty strings"""
        for lang_code, prompt in TABLE_SUMMARY_PROMPTS.items():
            self.assertIsInstance(prompt, str,
                                 f"Prompt for {lang_code} is not a string")
            self.assertGreater(len(prompt), 0,
                             f"Prompt for {lang_code} is empty")

    def test_table_summary_prompts_contain_key_instructions(self):
        """Test that table summary prompts contain key instructions for one-sentence summaries"""
        # Check Japanese prompt as reference
        ja_prompt = TABLE_SUMMARY_PROMPTS['ja']
        self.assertIn('1文', ja_prompt,
                     "Japanese prompt should request one sentence")
        self.assertIn('簡潔', ja_prompt,
                     "Japanese prompt should request conciseness")

        # Check English prompt
        en_prompt = TABLE_SUMMARY_PROMPTS['en']
        self.assertIn('one sentence', en_prompt.lower(),
                     "English prompt should request one sentence")


class TestI18nHelperTableSummaryPrompt(unittest.TestCase):
    """Tests for I18nHelper.get_table_summary_prompt() method"""

    def setUp(self):
        """Set up test fixtures"""
        self.i18n = I18nHelper()

    @patch('streamlit.session_state', {'language': 'ja'})
    def test_get_table_summary_prompt_japanese(self):
        """Test that get_table_summary_prompt returns Japanese prompt"""
        prompt = self.i18n.get_table_summary_prompt()
        self.assertEqual(prompt, TABLE_SUMMARY_PROMPTS['ja'])

    @patch('streamlit.session_state', {'language': 'en'})
    def test_get_table_summary_prompt_english(self):
        """Test that get_table_summary_prompt returns English prompt"""
        prompt = self.i18n.get_table_summary_prompt()
        self.assertEqual(prompt, TABLE_SUMMARY_PROMPTS['en'])

    @patch('streamlit.session_state', {'language': 'ko'})
    def test_get_table_summary_prompt_korean(self):
        """Test that get_table_summary_prompt returns Korean prompt"""
        prompt = self.i18n.get_table_summary_prompt()
        self.assertEqual(prompt, TABLE_SUMMARY_PROMPTS['ko'])

    @patch('streamlit.session_state', {'language': 'invalid_lang'})
    def test_get_table_summary_prompt_fallback_to_japanese(self):
        """Test that get_table_summary_prompt falls back to Japanese for invalid language"""
        prompt = self.i18n.get_table_summary_prompt()
        self.assertEqual(prompt, TABLE_SUMMARY_PROMPTS['ja'])


class TestSummarizeArticleForTable(unittest.TestCase):
    """Tests for summarize_article_for_table function"""

    def test_summarize_article_for_table_returns_string(self):
        """Test that summarize_article_for_table returns a string"""
        # Mock OpenAI client
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = "Test one-sentence summary"
        mock_client.chat.completions.create.return_value = mock_response

        # Sample article data
        article = {
            'title': 'Azure Load Testing',
            'products': ['Azure Load Testing'],
            'description': '<p>Azure Load Testing is now available in Switzerland North region.</p>'
        }

        system_prompt = "Summarize this in one sentence"
        deployment_name = 'gpt-4o'

        # Call the function
        result = azup.summarize_article_for_table(
            mock_client, deployment_name, article, system_prompt
        )

        # Verify the result
        self.assertIsInstance(result, str)
        self.assertEqual(result, "Test one-sentence summary")

        # Verify the client was called
        mock_client.chat.completions.create.assert_called_once()
        call_args = mock_client.chat.completions.create.call_args
        self.assertEqual(call_args[1]['model'], deployment_name)
        self.assertEqual(len(call_args[1]['messages']), 2)
        self.assertEqual(call_args[1]['messages'][0]['role'], 'system')
        self.assertEqual(call_args[1]['messages'][0]['content'], system_prompt)

    def test_summarize_article_for_table_with_multiple_products(self):
        """Test that summarize_article_for_table handles multiple products"""
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = "Multi-product summary"
        mock_client.chat.completions.create.return_value = mock_response

        article = {
            'title': 'Azure Update',
            'products': ['Azure Service A', 'Azure Service B', 'Azure Service C'],
            'description': '<p>Multiple products update</p>'
        }

        result = azup.summarize_article_for_table(
            mock_client, 'gpt-4o', article, "Test prompt"
        )

        self.assertIsNotNone(result)
        # Verify the user message contains product info
        call_args = mock_client.chat.completions.create.call_args
        user_message = call_args[1]['messages'][1]['content']
        self.assertIn('Azure Service A', user_message)
        self.assertIn('Azure Service B', user_message)
        self.assertIn('Azure Service C', user_message)

    def test_summarize_article_for_table_handles_html_description(self):
        """Test that summarize_article_for_table processes HTML in description"""
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = "Summary of HTML content"
        mock_client.chat.completions.create.return_value = mock_response

        article = {
            'title': 'Test',
            'products': ['Test Product'],
            'description': '<p>This is <strong>HTML</strong> content with <a href="https://example.com">links</a>.</p>'
        }

        result = azup.summarize_article_for_table(
            mock_client, 'gpt-4o', article, "Test prompt"
        )

        self.assertIsNotNone(result)
        # Verify HTML tags are removed from description in the user message
        call_args = mock_client.chat.completions.create.call_args
        user_message = call_args[1]['messages'][1]['content']
        # Should contain text without HTML tags
        self.assertIn('This is HTML content', user_message)
        self.assertNotIn('<p>', user_message)
        self.assertNotIn('<strong>', user_message)

    def test_summarize_article_for_table_handles_exception(self):
        """Test that summarize_article_for_table returns None on exception"""
        # Mock client that raises an exception
        mock_client = MagicMock()
        mock_client.chat.completions.create.side_effect = Exception("API Error")

        article = {
            'title': 'Test',
            'products': ['Test Product'],
            'description': '<p>Test description</p>'
        }

        result = azup.summarize_article_for_table(
            mock_client, 'gpt-4o', article, "Test prompt"
        )

        # Should return None on error
        self.assertIsNone(result)

    def test_summarize_article_for_table_extracts_links(self):
        """Test that summarize_article_for_table extracts links from description"""
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = "Summary with links"
        mock_client.chat.completions.create.return_value = mock_response

        article = {
            'title': 'Test',
            'products': ['Test Product'],
            'description': '<p>Content with <a href="https://docs.example.com/ref1">link 1</a> and <a href="https://docs.example.com/ref2">link 2</a>.</p>'
        }

        result = azup.summarize_article_for_table(
            mock_client, 'gpt-4o', article, "Test prompt"
        )

        self.assertIsNotNone(result)
        # Verify links are included in the user message
        call_args = mock_client.chat.completions.create.call_args
        user_message = call_args[1]['messages'][1]['content']
        self.assertIn('https://docs.example.com/ref1', user_message)
        self.assertIn('https://docs.example.com/ref2', user_message)
        self.assertIn('Links in description:', user_message)


if __name__ == '__main__':
    unittest.main()
