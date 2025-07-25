import unittest
from unittest.mock import patch, MagicMock
from i18n_helper import I18nHelper
from datetime import datetime


class TestI18nHelper(unittest.TestCase):

    def setUp(self):
        """Setup before tests"""
        # Mock Streamlit session state
        self.mock_session_state = {}

    def tearDown(self):
        """Cleanup after tests"""
        pass

    @patch('streamlit.session_state', new_callable=lambda: MagicMock())
    def test_translations_loading(self, mock_session_state):
        """Test translation file loading"""
        i18n = I18nHelper()
        self.assertIsNotNone(i18n.translations)
        self.assertIn('ja', i18n.translations)
        self.assertIn('en', i18n.translations)
        self.assertIn('ko', i18n.translations)
        self.assertIn('zh-cn', i18n.translations)
        self.assertIn('zh-tw', i18n.translations)

    @patch('streamlit.session_state', new_callable=lambda: {})
    def test_korean_translation(self, mock_session_state):
        """Test Korean translation"""
        mock_session_state['language'] = 'ko'

        i18n = I18nHelper()
        result = i18n.t('main_title')
        self.assertEqual(result, "Azure Updates 요약")

        # Button text test
        button_text = i18n.t('button_text')
        self.assertEqual(button_text, "데이터 가져오기")

    @patch('streamlit.session_state', new_callable=lambda: {})
    def test_chinese_simplified_translation(self, mock_session_state):
        """Test Chinese Simplified translation"""
        mock_session_state['language'] = 'zh-cn'

        i18n = I18nHelper()
        result = i18n.t('main_title')
        self.assertEqual(result, "Azure 更新摘要")

        # Button text test
        button_text = i18n.t('button_text')
        self.assertEqual(button_text, "获取数据")

    @patch('streamlit.session_state', new_callable=lambda: {})
    def test_chinese_traditional_translation(self, mock_session_state):
        """Test Chinese Traditional translation"""
        mock_session_state['language'] = 'zh-tw'

        i18n = I18nHelper()
        result = i18n.t('main_title')
        self.assertEqual(result, "Azure 更新摘要")

        # Button text test
        button_text = i18n.t('button_text')
        self.assertEqual(button_text, "取得資料")

    @patch('streamlit.session_state', new_callable=lambda: {})
    def test_english_translation(self, mock_session_state):
        """Test English translation"""
        mock_session_state['language'] = 'en'

        i18n = I18nHelper()
        result = i18n.t('main_title')
        self.assertEqual(result, "Azure Updates Summary")

        # Button text test
        button_text = i18n.t('button_text')
        self.assertEqual(button_text, "Get Data")


class TestLanguageDetection(unittest.TestCase):

    @patch('streamlit.session_state', new_callable=lambda: MagicMock())
    def test_browser_language_detection_from_session(self, mock_session_state):
        """Test browser language detection from session state"""
        mock_session_state.__contains__ = lambda self, key: key == 'browser_detected_lang'
        mock_session_state.browser_detected_lang = 'ja'
        mock_session_state.detected_browser_language = None

        i18n = I18nHelper()
        detected_lang = i18n._detect_browser_language()
        self.assertEqual(detected_lang, 'ja')

    @patch('streamlit.session_state', new_callable=lambda: MagicMock())
    def test_browser_language_detection_default_to_english(self, mock_session_state):
        """Test browser language detection defaults to English when no detection"""
        mock_session_state.__contains__ = lambda self, key: False

        i18n = I18nHelper()
        detected_lang = i18n._detect_browser_language()
        self.assertEqual(detected_lang, 'en')

    @patch('streamlit.session_state', new_callable=lambda: MagicMock())
    def test_browser_language_detection_cached(self, mock_session_state):
        """Test browser language detection uses cached value"""
        mock_session_state.__contains__ = lambda self, key: key == 'detected_browser_language'
        mock_session_state.detected_browser_language = 'ko'

        i18n = I18nHelper()
        detected_lang = i18n._detect_browser_language()
        self.assertEqual(detected_lang, 'ko')


class TestSystemPrompts(unittest.TestCase):

    @patch('streamlit.session_state', new_callable=lambda: {})
    def test_korean_system_prompt(self, mock_session_state):
        """Test Korean system prompt"""
        mock_session_state['language'] = 'ko'

        i18n = I18nHelper()
        prompt = i18n.get_system_prompt()
        self.assertIn('한국어로', prompt)
        self.assertIn('3줄 정도로', prompt)

    @patch('streamlit.session_state', new_callable=lambda: {})
    def test_chinese_simplified_system_prompt(self, mock_session_state):
        """Test Chinese Simplified system prompt"""
        mock_session_state['language'] = 'zh-cn'

        i18n = I18nHelper()
        prompt = i18n.get_system_prompt()
        self.assertIn('中文(简体)', prompt)
        self.assertIn('大约 3 行', prompt)

    @patch('streamlit.session_state', new_callable=lambda: {})
    def test_chinese_traditional_system_prompt(self, mock_session_state):
        """Test Chinese Traditional system prompt"""
        mock_session_state['language'] = 'zh-tw'

        i18n = I18nHelper()
        prompt = i18n.get_system_prompt()
        self.assertIn('中文(繁體)', prompt)
        self.assertIn('大約 3 行', prompt)

    @patch('streamlit.session_state', new_callable=lambda: {})
    def test_english_system_prompt(self, mock_session_state):
        """Test English system prompt"""
        mock_session_state['language'] = 'en'

        i18n = I18nHelper()
        prompt = i18n.get_system_prompt()
        self.assertIn('in English', prompt)
        self.assertIn('about 3 lines', prompt)


class TestDateFormatting(unittest.TestCase):

    def setUp(self):
        """Prepare test date"""
        self.test_date = datetime(2025, 7, 25, 14, 30, 0)

    @patch('streamlit.session_state', new_callable=lambda: {})
    def test_korean_date_format(self, mock_session_state):
        """Test Korean date format"""
        mock_session_state['language'] = 'ko'

        i18n = I18nHelper()
        formatted_date = i18n.format_date(self.test_date)
        self.assertEqual(formatted_date, "2025년 07월 25일")

    @patch('streamlit.session_state', new_callable=lambda: {})
    def test_chinese_simplified_date_format(self, mock_session_state):
        """Test Chinese Simplified date format"""
        mock_session_state['language'] = 'zh-cn'

        i18n = I18nHelper()
        formatted_date = i18n.format_date(self.test_date)
        self.assertEqual(formatted_date, "2025年07月25日")

    @patch('streamlit.session_state', new_callable=lambda: {})
    def test_chinese_traditional_date_format(self, mock_session_state):
        """Test Chinese Traditional date format"""
        mock_session_state['language'] = 'zh-tw'

        i18n = I18nHelper()
        formatted_date = i18n.format_date(self.test_date)
        self.assertEqual(formatted_date, "2025年07月25日")

    @patch('streamlit.session_state', new_callable=lambda: {})
    def test_english_date_format(self, mock_session_state):
        """Test English date format"""
        mock_session_state['language'] = 'en'

        i18n = I18nHelper()
        formatted_date = i18n.format_date(self.test_date)
        self.assertEqual(formatted_date, "July 25, 2025")


class TestPlaceholderReplacement(unittest.TestCase):

    @patch('streamlit.session_state', new_callable=lambda: {})
    def test_korean_placeholder_replacement(self, mock_session_state):
        """Test Korean placeholder replacement"""
        mock_session_state['language'] = 'ko'

        i18n = I18nHelper()
        result = i18n.t('update_count', count=5)
        self.assertEqual(result, "업데이트가 5개 있습니다.")

    @patch('streamlit.session_state', new_callable=lambda: {})
    def test_chinese_simplified_placeholder_replacement(self, mock_session_state):
        """Test Chinese Simplified placeholder replacement"""
        mock_session_state['language'] = 'zh-cn'

        i18n = I18nHelper()
        result = i18n.t('update_count', count=5)
        self.assertEqual(result, "有 5 个更新。")

    @patch('streamlit.session_state', new_callable=lambda: {})
    def test_chinese_traditional_placeholder_replacement(self, mock_session_state):
        """Test Chinese Traditional placeholder replacement"""
        mock_session_state['language'] = 'zh-tw'

        i18n = I18nHelper()
        result = i18n.t('update_count', count=5)
        self.assertEqual(result, "有 5 個更新。")

    @patch('streamlit.session_state', new_callable=lambda: {})
    def test_english_placeholder_replacement(self, mock_session_state):
        """Test English placeholder replacement"""
        mock_session_state['language'] = 'en'

        i18n = I18nHelper()
        result = i18n.t('update_count', count=5)
        self.assertEqual(result, "There are 5 updates.")


if __name__ == '__main__':
    unittest.main()