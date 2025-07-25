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
    @patch('locale.getdefaultlocale')
    def test_japanese_locale_detection(self, mock_locale, mock_session_state):
        """Test Japanese locale detection"""
        mock_locale.return_value = ('ja_JP', 'UTF-8')
        mock_session_state.__contains__ = lambda key: False
        mock_session_state.__setitem__ = lambda key, value: None

        i18n = I18nHelper()
        detected_lang = i18n._detect_system_locale()
        self.assertEqual(detected_lang, 'ja')

    @patch('streamlit.session_state', new_callable=lambda: MagicMock())
    @patch('locale.getdefaultlocale')
    def test_korean_locale_detection(self, mock_locale, mock_session_state):
        """Test Korean locale detection"""
        mock_locale.return_value = ('ko_KR', 'UTF-8')
        mock_session_state.__contains__ = lambda key: False
        mock_session_state.__setitem__ = lambda key, value: None

        i18n = I18nHelper()
        detected_lang = i18n._detect_system_locale()
        self.assertEqual(detected_lang, 'ko')

    @patch('streamlit.session_state', new_callable=lambda: MagicMock())
    @patch('locale.getdefaultlocale')
    def test_chinese_simplified_locale_detection(self, mock_locale, mock_session_state):
        """Test Chinese Simplified locale detection"""
        mock_locale.return_value = ('zh_CN', 'UTF-8')
        mock_session_state.__contains__ = lambda key: False
        mock_session_state.__setitem__ = lambda key, value: None

        i18n = I18nHelper()
        detected_lang = i18n._detect_system_locale()
        self.assertEqual(detected_lang, 'zh-cn')

    @patch('streamlit.session_state', new_callable=lambda: MagicMock())
    @patch('locale.getdefaultlocale')
    def test_chinese_traditional_locale_detection(self, mock_locale, mock_session_state):
        """Test Chinese Traditional locale detection"""
        mock_locale.return_value = ('zh_TW', 'UTF-8')
        mock_session_state.__contains__ = lambda key: False
        mock_session_state.__setitem__ = lambda key, value: None

        i18n = I18nHelper()
        detected_lang = i18n._detect_system_locale()
        self.assertEqual(detected_lang, 'zh-tw')

    @patch('streamlit.session_state', new_callable=lambda: MagicMock())
    @patch('locale.getdefaultlocale')
    def test_chinese_hongkong_locale_detection(self, mock_locale, mock_session_state):
        """Test Chinese Hong Kong locale detection (treated as Traditional Chinese)"""
        mock_locale.return_value = ('zh_HK', 'UTF-8')
        mock_session_state.__contains__ = lambda key: False
        mock_session_state.__setitem__ = lambda key, value: None

        i18n = I18nHelper()
        detected_lang = i18n._detect_system_locale()
        self.assertEqual(detected_lang, 'zh-tw')

    @patch('streamlit.session_state', new_callable=lambda: MagicMock())
    @patch('locale.getdefaultlocale')
    def test_english_us_locale_detection(self, mock_locale, mock_session_state):
        """Test English (US) locale detection"""
        mock_locale.return_value = ('en_US', 'UTF-8')
        mock_session_state.__contains__ = lambda key: False
        mock_session_state.__setitem__ = lambda key, value: None

        i18n = I18nHelper()
        detected_lang = i18n._detect_system_locale()
        self.assertEqual(detected_lang, 'en')

    @patch('streamlit.session_state', new_callable=lambda: MagicMock())
    @patch('locale.getdefaultlocale')
    def test_english_gb_locale_detection(self, mock_locale, mock_session_state):
        """Test English (GB) locale detection"""
        mock_locale.return_value = ('en_GB', 'UTF-8')
        mock_session_state.__contains__ = lambda key: False
        mock_session_state.__setitem__ = lambda key, value: None

        i18n = I18nHelper()
        detected_lang = i18n._detect_system_locale()
        self.assertEqual(detected_lang, 'en')

    @patch('streamlit.session_state', new_callable=lambda: MagicMock())
    @patch('locale.getdefaultlocale')
    def test_chinese_generic_locale_detection(self, mock_locale, mock_session_state):
        """Test Chinese (generic) locale detection (treated as Simplified Chinese)"""
        mock_locale.return_value = ('zh', 'UTF-8')
        mock_session_state.__contains__ = lambda key: False
        mock_session_state.__setitem__ = lambda key, value: None

        i18n = I18nHelper()
        detected_lang = i18n._detect_system_locale()
        self.assertEqual(detected_lang, 'zh-cn')

    @patch('streamlit.session_state', new_callable=lambda: MagicMock())
    @patch('locale.getdefaultlocale')
    def test_thai_locale_detection(self, mock_locale, mock_session_state):
        """Test Thai locale detection"""
        mock_locale.return_value = ('th_TH', 'UTF-8')
        mock_session_state.__contains__ = lambda key: False
        mock_session_state.__setitem__ = lambda key, value: None

        i18n = I18nHelper()
        detected_lang = i18n._detect_system_locale()
        self.assertEqual(detected_lang, 'th')

    @patch('streamlit.session_state', new_callable=lambda: MagicMock())
    @patch('locale.getdefaultlocale')
    def test_vietnamese_locale_detection(self, mock_locale, mock_session_state):
        """Test Vietnamese locale detection"""
        mock_locale.return_value = ('vi_VN', 'UTF-8')
        mock_session_state.__contains__ = lambda key: False
        mock_session_state.__setitem__ = lambda key, value: None

        i18n = I18nHelper()
        detected_lang = i18n._detect_system_locale()
        self.assertEqual(detected_lang, 'vi')

    @patch('streamlit.session_state', new_callable=lambda: MagicMock())
    @patch('locale.getdefaultlocale')
    def test_indonesian_locale_detection(self, mock_locale, mock_session_state):
        """Test Indonesian locale detection"""
        mock_locale.return_value = ('id_ID', 'UTF-8')
        mock_session_state.__contains__ = lambda key: False
        mock_session_state.__setitem__ = lambda key, value: None

        i18n = I18nHelper()
        detected_lang = i18n._detect_system_locale()
        self.assertEqual(detected_lang, 'id')

    @patch('streamlit.session_state', new_callable=lambda: MagicMock())
    @patch('locale.getdefaultlocale')
    def test_hindi_locale_detection(self, mock_locale, mock_session_state):
        """Test Hindi locale detection"""
        mock_locale.return_value = ('hi_IN', 'UTF-8')
        mock_session_state.__contains__ = lambda key: False
        mock_session_state.__setitem__ = lambda key, value: None

        i18n = I18nHelper()
        detected_lang = i18n._detect_system_locale()
        self.assertEqual(detected_lang, 'hi')

    @patch('streamlit.session_state', new_callable=lambda: MagicMock())
    @patch('locale.getdefaultlocale')
    def test_unsupported_locale_detection(self, mock_locale, mock_session_state):
        """Test unsupported locale detection (defaults to English)"""
        mock_locale.return_value = ('fr_FR', 'UTF-8')
        mock_session_state.__contains__ = lambda key: False
        mock_session_state.__setitem__ = lambda key, value: None

        i18n = I18nHelper()
        detected_lang = i18n._detect_system_locale()
        self.assertEqual(detected_lang, 'en')

    @patch('streamlit.session_state', new_callable=lambda: MagicMock())
    @patch('locale.getdefaultlocale')
    def test_thai_generic_locale_detection(self, mock_locale, mock_session_state):
        """Test Thai (generic) locale detection"""
        mock_locale.return_value = ('th', 'UTF-8')
        mock_session_state.__contains__ = lambda key: False
        mock_session_state.__setitem__ = lambda key, value: None

        i18n = I18nHelper()
        detected_lang = i18n._detect_system_locale()
        self.assertEqual(detected_lang, 'th')

    @patch('streamlit.session_state', new_callable=lambda: MagicMock())
    @patch('locale.getdefaultlocale')
    def test_vietnamese_generic_locale_detection(self, mock_locale, mock_session_state):
        """Test Vietnamese (generic) locale detection"""
        mock_locale.return_value = ('vi', 'UTF-8')
        mock_session_state.__contains__ = lambda key: False
        mock_session_state.__setitem__ = lambda key, value: None

        i18n = I18nHelper()
        detected_lang = i18n._detect_system_locale()
        self.assertEqual(detected_lang, 'vi')

    @patch('streamlit.session_state', new_callable=lambda: MagicMock())
    @patch('locale.getdefaultlocale')
    def test_indonesian_generic_locale_detection(self, mock_locale, mock_session_state):
        """Test Indonesian (generic) locale detection"""
        mock_locale.return_value = ('id', 'UTF-8')
        mock_session_state.__contains__ = lambda key: False
        mock_session_state.__setitem__ = lambda key, value: None

        i18n = I18nHelper()
        detected_lang = i18n._detect_system_locale()
        self.assertEqual(detected_lang, 'id')

    @patch('streamlit.session_state', new_callable=lambda: MagicMock())
    @patch('locale.getdefaultlocale')
    def test_hindi_generic_locale_detection(self, mock_locale, mock_session_state):
        """Test Hindi (generic) locale detection"""
        mock_locale.return_value = ('hi', 'UTF-8')
        mock_session_state.__contains__ = lambda key: False
        mock_session_state.__setitem__ = lambda key, value: None

        i18n = I18nHelper()
        detected_lang = i18n._detect_system_locale()
        self.assertEqual(detected_lang, 'hi')

    @patch('streamlit.session_state', new_callable=lambda: MagicMock())
    @patch('locale.getdefaultlocale')
    def test_korean_region_locale_detection(self, mock_locale, mock_session_state):
        """Test Korean (region-specific) locale detection"""
        mock_locale.return_value = ('ko_KR', 'UTF-8')
        mock_session_state.__contains__ = lambda key: False
        mock_session_state.__setitem__ = lambda key, value: None

        i18n = I18nHelper()
        detected_lang = i18n._detect_system_locale()
        self.assertEqual(detected_lang, 'ko')

    @patch('streamlit.session_state', new_callable=lambda: MagicMock())
    @patch('locale.getdefaultlocale')
    def test_korean_generic_locale_detection(self, mock_locale, mock_session_state):
        """Test Korean (generic) locale detection"""
        mock_locale.return_value = ('ko', 'UTF-8')
        mock_session_state.__contains__ = lambda key: False
        mock_session_state.__setitem__ = lambda key, value: None

        i18n = I18nHelper()
        detected_lang = i18n._detect_system_locale()
        self.assertEqual(detected_lang, 'ko')

    @patch('streamlit.session_state', new_callable=lambda: MagicMock())
    @patch('locale.getdefaultlocale')
    def test_chinese_cn_region_locale_detection(self, mock_locale, mock_session_state):
        """Test Chinese (mainland China) locale detection"""
        mock_locale.return_value = ('zh_CN', 'UTF-8')
        mock_session_state.__contains__ = lambda key: False
        mock_session_state.__setitem__ = lambda key, value: None

        i18n = I18nHelper()
        detected_lang = i18n._detect_system_locale()
        self.assertEqual(detected_lang, 'zh-cn')

    @patch('streamlit.session_state', new_callable=lambda: MagicMock())
    @patch('locale.getdefaultlocale')
    def test_japanese_region_locale_detection(self, mock_locale, mock_session_state):
        """Test Japanese (region-specific) locale detection"""
        mock_locale.return_value = ('ja_JP', 'UTF-8')
        mock_session_state.__contains__ = lambda key: False
        mock_session_state.__setitem__ = lambda key, value: None

        i18n = I18nHelper()
        detected_lang = i18n._detect_system_locale()
        self.assertEqual(detected_lang, 'ja')

    @patch('streamlit.session_state', new_callable=lambda: MagicMock())
    @patch('locale.getdefaultlocale')
    def test_japanese_generic_locale_detection(self, mock_locale, mock_session_state):
        """Test Japanese (generic) locale detection"""
        mock_locale.return_value = ('ja', 'UTF-8')
        mock_session_state.__contains__ = lambda key: False
        mock_session_state.__setitem__ = lambda key, value: None

        i18n = I18nHelper()
        detected_lang = i18n._detect_system_locale()
        self.assertEqual(detected_lang, 'ja')

    @patch('streamlit.session_state', new_callable=lambda: MagicMock())
    @patch('locale.getdefaultlocale')
    def test_english_generic_locale_detection(self, mock_locale, mock_session_state):
        """Test English (generic) locale detection"""
        mock_locale.return_value = ('en', 'UTF-8')
        mock_session_state.__contains__ = lambda key: False
        mock_session_state.__setitem__ = lambda key, value: None

        i18n = I18nHelper()
        detected_lang = i18n._detect_system_locale()
        self.assertEqual(detected_lang, 'en')

    @patch('streamlit.session_state', new_callable=lambda: MagicMock())
    @patch('locale.getdefaultlocale')
    def test_none_locale_detection(self, mock_locale, mock_session_state):
        """Test when locale is None (defaults to English)"""
        mock_locale.return_value = (None, None)
        mock_session_state.__contains__ = lambda key: False
        mock_session_state.__setitem__ = lambda key, value: None

        i18n = I18nHelper()
        detected_lang = i18n._detect_system_locale()
        self.assertEqual(detected_lang, 'en')


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
