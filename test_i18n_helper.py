import unittest
import os
import json
from unittest.mock import patch, MagicMock
import streamlit as st
from i18n_helper import I18nHelper, LANGUAGES, SYSTEM_PROMPTS, DATE_FORMATS
from datetime import datetime


class TestI18nHelper(unittest.TestCase):
    
    def setUp(self):
        """テストの前準備"""
        # Mock Streamlit session state
        self.mock_session_state = {}
        
    def tearDown(self):
        """テスト後のクリーンアップ"""
        pass
    
    @patch('streamlit.session_state', new_callable=lambda: MagicMock())
    def test_translations_loading(self, mock_session_state):
        """翻訳ファイルの読み込みテスト"""
        i18n = I18nHelper()
        self.assertIsNotNone(i18n.translations)
        self.assertIn('ja', i18n.translations)
        self.assertIn('en', i18n.translations)
        self.assertIn('ko', i18n.translations)
        self.assertIn('zh-cn', i18n.translations)
        self.assertIn('zh-tw', i18n.translations)
    
    @patch('streamlit.session_state', new_callable=lambda: {})
    def test_korean_translation(self, mock_session_state):
        """韓国語翻訳のテスト"""
        mock_session_state['language'] = 'ko'
        
        i18n = I18nHelper()
        result = i18n.t('main_title')
        self.assertEqual(result, "Azure Updates 요약")
        
        # Button text test
        button_text = i18n.t('button_text')
        self.assertEqual(button_text, "데이터 가져오기")
    
    @patch('streamlit.session_state', new_callable=lambda: {})
    def test_chinese_simplified_translation(self, mock_session_state):
        """中国語簡体字翻訳のテスト"""
        mock_session_state['language'] = 'zh-cn'
        
        i18n = I18nHelper()
        result = i18n.t('main_title')
        self.assertEqual(result, "Azure 更新摘要")
        
        # Button text test
        button_text = i18n.t('button_text')
        self.assertEqual(button_text, "获取数据")
    
    @patch('streamlit.session_state', new_callable=lambda: {})
    def test_chinese_traditional_translation(self, mock_session_state):
        """中国語繁体字翻訳のテスト"""
        mock_session_state['language'] = 'zh-tw'
        
        i18n = I18nHelper()
        result = i18n.t('main_title')
        self.assertEqual(result, "Azure 更新摘要")
        
        # Button text test
        button_text = i18n.t('button_text')
        self.assertEqual(button_text, "取得資料")
    
    @patch('streamlit.session_state', new_callable=lambda: {})
    def test_english_translation(self, mock_session_state):
        """英語翻訳のテスト"""
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
        """日本語ロケール検出のテスト"""
        mock_locale.return_value = ('ja_JP', 'UTF-8')
        mock_session_state.__contains__ = lambda key: False
        mock_session_state.__setitem__ = lambda key, value: None
        
        i18n = I18nHelper()
        detected_lang = i18n._detect_system_locale()
        self.assertEqual(detected_lang, 'ja')
    
    @patch('streamlit.session_state', new_callable=lambda: MagicMock())
    @patch('locale.getdefaultlocale')
    def test_korean_locale_detection(self, mock_locale, mock_session_state):
        """韓国語ロケール検出のテスト"""
        mock_locale.return_value = ('ko_KR', 'UTF-8')
        mock_session_state.__contains__ = lambda key: False
        mock_session_state.__setitem__ = lambda key, value: None
        
        i18n = I18nHelper()
        detected_lang = i18n._detect_system_locale()
        self.assertEqual(detected_lang, 'ko')
    
    @patch('streamlit.session_state', new_callable=lambda: MagicMock())
    @patch('locale.getdefaultlocale')
    def test_chinese_simplified_locale_detection(self, mock_locale, mock_session_state):
        """中国語簡体字ロケール検出のテスト"""
        mock_locale.return_value = ('zh_CN', 'UTF-8')
        mock_session_state.__contains__ = lambda key: False
        mock_session_state.__setitem__ = lambda key, value: None
        
        i18n = I18nHelper()
        detected_lang = i18n._detect_system_locale()
        self.assertEqual(detected_lang, 'zh-cn')
    
    @patch('streamlit.session_state', new_callable=lambda: MagicMock())
    @patch('locale.getdefaultlocale')
    def test_chinese_traditional_locale_detection(self, mock_locale, mock_session_state):
        """中国語繁体字ロケール検出のテスト"""
        mock_locale.return_value = ('zh_TW', 'UTF-8')
        mock_session_state.__contains__ = lambda key: False
        mock_session_state.__setitem__ = lambda key, value: None
        
        i18n = I18nHelper()
        detected_lang = i18n._detect_system_locale()
        self.assertEqual(detected_lang, 'zh-tw')
    
    @patch('streamlit.session_state', new_callable=lambda: MagicMock())
    @patch('locale.getdefaultlocale')
    def test_chinese_hongkong_locale_detection(self, mock_locale, mock_session_state):
        """中国語香港ロケール検出のテスト（繁体字として扱う）"""
        mock_locale.return_value = ('zh_HK', 'UTF-8')
        mock_session_state.__contains__ = lambda key: False
        mock_session_state.__setitem__ = lambda key, value: None
        
        i18n = I18nHelper()
        detected_lang = i18n._detect_system_locale()
        self.assertEqual(detected_lang, 'zh-tw')
    
    @patch('streamlit.session_state', new_callable=lambda: MagicMock())
    @patch('locale.getdefaultlocale')
    def test_english_us_locale_detection(self, mock_locale, mock_session_state):
        """英語（米国）ロケール検出のテスト"""
        mock_locale.return_value = ('en_US', 'UTF-8')
        mock_session_state.__contains__ = lambda key: False
        mock_session_state.__setitem__ = lambda key, value: None
        
        i18n = I18nHelper()
        detected_lang = i18n._detect_system_locale()
        self.assertEqual(detected_lang, 'en')
    
    @patch('streamlit.session_state', new_callable=lambda: MagicMock())
    @patch('locale.getdefaultlocale')
    def test_english_gb_locale_detection(self, mock_locale, mock_session_state):
        """英語（英国）ロケール検出のテスト"""
        mock_locale.return_value = ('en_GB', 'UTF-8')
        mock_session_state.__contains__ = lambda key: False
        mock_session_state.__setitem__ = lambda key, value: None
        
        i18n = I18nHelper()
        detected_lang = i18n._detect_system_locale()
        self.assertEqual(detected_lang, 'en')
    
    @patch('streamlit.session_state', new_callable=lambda: MagicMock())
    @patch('locale.getdefaultlocale')
    def test_chinese_generic_locale_detection(self, mock_locale, mock_session_state):
        """中国語（汎用）ロケール検出のテスト（簡体字として扱う）"""
        mock_locale.return_value = ('zh', 'UTF-8')
        mock_session_state.__contains__ = lambda key: False
        mock_session_state.__setitem__ = lambda key, value: None
        
        i18n = I18nHelper()
        detected_lang = i18n._detect_system_locale()
        self.assertEqual(detected_lang, 'zh-cn')
    
    @patch('streamlit.session_state', new_callable=lambda: MagicMock())
    @patch('locale.getdefaultlocale')
    def test_thai_locale_detection(self, mock_locale, mock_session_state):
        """タイ語ロケール検出のテスト"""
        mock_locale.return_value = ('th_TH', 'UTF-8')
        mock_session_state.__contains__ = lambda key: False
        mock_session_state.__setitem__ = lambda key, value: None
        
        i18n = I18nHelper()
        detected_lang = i18n._detect_system_locale()
        self.assertEqual(detected_lang, 'th')
    
    @patch('streamlit.session_state', new_callable=lambda: MagicMock())
    @patch('locale.getdefaultlocale')
    def test_vietnamese_locale_detection(self, mock_locale, mock_session_state):
        """ベトナム語ロケール検出のテスト"""
        mock_locale.return_value = ('vi_VN', 'UTF-8')
        mock_session_state.__contains__ = lambda key: False
        mock_session_state.__setitem__ = lambda key, value: None
        
        i18n = I18nHelper()
        detected_lang = i18n._detect_system_locale()
        self.assertEqual(detected_lang, 'vi')
    
    @patch('streamlit.session_state', new_callable=lambda: MagicMock())
    @patch('locale.getdefaultlocale')
    def test_indonesian_locale_detection(self, mock_locale, mock_session_state):
        """インドネシア語ロケール検出のテスト"""
        mock_locale.return_value = ('id_ID', 'UTF-8')
        mock_session_state.__contains__ = lambda key: False
        mock_session_state.__setitem__ = lambda key, value: None
        
        i18n = I18nHelper()
        detected_lang = i18n._detect_system_locale()
        self.assertEqual(detected_lang, 'id')
    
    @patch('streamlit.session_state', new_callable=lambda: MagicMock())
    @patch('locale.getdefaultlocale')
    def test_hindi_locale_detection(self, mock_locale, mock_session_state):
        """ヒンディー語ロケール検出のテスト"""
        mock_locale.return_value = ('hi_IN', 'UTF-8')
        mock_session_state.__contains__ = lambda key: False
        mock_session_state.__setitem__ = lambda key, value: None
        
        i18n = I18nHelper()
        detected_lang = i18n._detect_system_locale()
        self.assertEqual(detected_lang, 'hi')
    
    @patch('streamlit.session_state', new_callable=lambda: MagicMock())
    @patch('locale.getdefaultlocale')
    def test_unsupported_locale_detection(self, mock_locale, mock_session_state):
        """サポート外ロケール検出のテスト（デフォルト英語）"""
        mock_locale.return_value = ('fr_FR', 'UTF-8')
        mock_session_state.__contains__ = lambda key: False
        mock_session_state.__setitem__ = lambda key, value: None
        
        i18n = I18nHelper()
        detected_lang = i18n._detect_system_locale()
        self.assertEqual(detected_lang, 'en')
    
    @patch('streamlit.session_state', new_callable=lambda: MagicMock())
    @patch('locale.getdefaultlocale')
    def test_thai_generic_locale_detection(self, mock_locale, mock_session_state):
        """タイ語（汎用）ロケール検出のテスト"""
        mock_locale.return_value = ('th', 'UTF-8')
        mock_session_state.__contains__ = lambda key: False
        mock_session_state.__setitem__ = lambda key, value: None
        
        i18n = I18nHelper()
        detected_lang = i18n._detect_system_locale()
        self.assertEqual(detected_lang, 'th')
    
    @patch('streamlit.session_state', new_callable=lambda: MagicMock())
    @patch('locale.getdefaultlocale')
    def test_vietnamese_generic_locale_detection(self, mock_locale, mock_session_state):
        """ベトナム語（汎用）ロケール検出のテスト"""
        mock_locale.return_value = ('vi', 'UTF-8')
        mock_session_state.__contains__ = lambda key: False
        mock_session_state.__setitem__ = lambda key, value: None
        
        i18n = I18nHelper()
        detected_lang = i18n._detect_system_locale()
        self.assertEqual(detected_lang, 'vi')
    
    @patch('streamlit.session_state', new_callable=lambda: MagicMock())
    @patch('locale.getdefaultlocale')
    def test_indonesian_generic_locale_detection(self, mock_locale, mock_session_state):
        """インドネシア語（汎用）ロケール検出のテスト"""
        mock_locale.return_value = ('id', 'UTF-8')
        mock_session_state.__contains__ = lambda key: False
        mock_session_state.__setitem__ = lambda key, value: None
        
        i18n = I18nHelper()
        detected_lang = i18n._detect_system_locale()
        self.assertEqual(detected_lang, 'id')
    
    @patch('streamlit.session_state', new_callable=lambda: MagicMock())
    @patch('locale.getdefaultlocale')
    def test_hindi_generic_locale_detection(self, mock_locale, mock_session_state):
        """ヒンディー語（汎用）ロケール検出のテスト"""
        mock_locale.return_value = ('hi', 'UTF-8')
        mock_session_state.__contains__ = lambda key: False
        mock_session_state.__setitem__ = lambda key, value: None
        
        i18n = I18nHelper()
        detected_lang = i18n._detect_system_locale()
        self.assertEqual(detected_lang, 'hi')
    
    @patch('streamlit.session_state', new_callable=lambda: MagicMock())
    @patch('locale.getdefaultlocale')
    def test_korean_region_locale_detection(self, mock_locale, mock_session_state):
        """韓国語（地域指定）ロケール検出のテスト"""
        mock_locale.return_value = ('ko_KR', 'UTF-8')
        mock_session_state.__contains__ = lambda key: False
        mock_session_state.__setitem__ = lambda key, value: None
        
        i18n = I18nHelper()
        detected_lang = i18n._detect_system_locale()
        self.assertEqual(detected_lang, 'ko')
    
    @patch('streamlit.session_state', new_callable=lambda: MagicMock())
    @patch('locale.getdefaultlocale')
    def test_korean_generic_locale_detection(self, mock_locale, mock_session_state):
        """韓国語（汎用）ロケール検出のテスト"""
        mock_locale.return_value = ('ko', 'UTF-8')
        mock_session_state.__contains__ = lambda key: False
        mock_session_state.__setitem__ = lambda key, value: None
        
        i18n = I18nHelper()
        detected_lang = i18n._detect_system_locale()
        self.assertEqual(detected_lang, 'ko')
    
    @patch('streamlit.session_state', new_callable=lambda: MagicMock())
    @patch('locale.getdefaultlocale')
    def test_chinese_cn_region_locale_detection(self, mock_locale, mock_session_state):
        """中国語（中国本土）ロケール検出のテスト"""
        mock_locale.return_value = ('zh_CN', 'UTF-8')
        mock_session_state.__contains__ = lambda key: False
        mock_session_state.__setitem__ = lambda key, value: None
        
        i18n = I18nHelper()
        detected_lang = i18n._detect_system_locale()
        self.assertEqual(detected_lang, 'zh-cn')
    
    @patch('streamlit.session_state', new_callable=lambda: MagicMock())
    @patch('locale.getdefaultlocale')
    def test_japanese_region_locale_detection(self, mock_locale, mock_session_state):
        """日本語（地域指定）ロケール検出のテスト"""
        mock_locale.return_value = ('ja_JP', 'UTF-8')
        mock_session_state.__contains__ = lambda key: False
        mock_session_state.__setitem__ = lambda key, value: None
        
        i18n = I18nHelper()
        detected_lang = i18n._detect_system_locale()
        self.assertEqual(detected_lang, 'ja')
    
    @patch('streamlit.session_state', new_callable=lambda: MagicMock())
    @patch('locale.getdefaultlocale')
    def test_japanese_generic_locale_detection(self, mock_locale, mock_session_state):
        """日本語（汎用）ロケール検出のテスト"""
        mock_locale.return_value = ('ja', 'UTF-8')
        mock_session_state.__contains__ = lambda key: False
        mock_session_state.__setitem__ = lambda key, value: None
        
        i18n = I18nHelper()
        detected_lang = i18n._detect_system_locale()
        self.assertEqual(detected_lang, 'ja')
    
    @patch('streamlit.session_state', new_callable=lambda: MagicMock())
    @patch('locale.getdefaultlocale')
    def test_english_generic_locale_detection(self, mock_locale, mock_session_state):
        """英語（汎用）ロケール検出のテスト"""
        mock_locale.return_value = ('en', 'UTF-8')
        mock_session_state.__contains__ = lambda key: False
        mock_session_state.__setitem__ = lambda key, value: None
        
        i18n = I18nHelper()
        detected_lang = i18n._detect_system_locale()
        self.assertEqual(detected_lang, 'en')
    
    @patch('streamlit.session_state', new_callable=lambda: MagicMock())
    @patch('locale.getdefaultlocale')
    def test_none_locale_detection(self, mock_locale, mock_session_state):
        """ロケールがNoneの場合のテスト（デフォルト英語）"""
        mock_locale.return_value = (None, None)
        mock_session_state.__contains__ = lambda key: False
        mock_session_state.__setitem__ = lambda key, value: None
        
        i18n = I18nHelper()
        detected_lang = i18n._detect_system_locale()
        self.assertEqual(detected_lang, 'en')


class TestSystemPrompts(unittest.TestCase):
    
    @patch('streamlit.session_state', new_callable=lambda: {})
    def test_korean_system_prompt(self, mock_session_state):
        """韓国語システムプロンプトのテスト"""
        mock_session_state['language'] = 'ko'
        
        i18n = I18nHelper()
        prompt = i18n.get_system_prompt()
        self.assertIn('한국어로', prompt)
        self.assertIn('3줄 정도로', prompt)
    
    @patch('streamlit.session_state', new_callable=lambda: {})
    def test_chinese_simplified_system_prompt(self, mock_session_state):
        """中国語簡体字システムプロンプトのテスト"""
        mock_session_state['language'] = 'zh-cn'
        
        i18n = I18nHelper()
        prompt = i18n.get_system_prompt()
        self.assertIn('中文(简体)', prompt)
        self.assertIn('大约 3 行', prompt)
    
    @patch('streamlit.session_state', new_callable=lambda: {})
    def test_chinese_traditional_system_prompt(self, mock_session_state):
        """中国語繁体字システムプロンプトのテスト"""
        mock_session_state['language'] = 'zh-tw'
        
        i18n = I18nHelper()
        prompt = i18n.get_system_prompt()
        self.assertIn('中文(繁體)', prompt)
        self.assertIn('大約 3 行', prompt)
    
    @patch('streamlit.session_state', new_callable=lambda: {})
    def test_english_system_prompt(self, mock_session_state):
        """英語システムプロンプトのテスト"""
        mock_session_state['language'] = 'en'
        
        i18n = I18nHelper()
        prompt = i18n.get_system_prompt()
        self.assertIn('in English', prompt)
        self.assertIn('about 3 lines', prompt)


class TestDateFormatting(unittest.TestCase):
    
    def setUp(self):
        """テスト用の日付を準備"""
        self.test_date = datetime(2025, 7, 25, 14, 30, 0)
    
    @patch('streamlit.session_state', new_callable=lambda: {})
    def test_korean_date_format(self, mock_session_state):
        """韓国語日付フォーマットのテスト"""
        mock_session_state['language'] = 'ko'
        
        i18n = I18nHelper()
        formatted_date = i18n.format_date(self.test_date)
        self.assertEqual(formatted_date, "2025년 07월 25일")
    
    @patch('streamlit.session_state', new_callable=lambda: {})
    def test_chinese_simplified_date_format(self, mock_session_state):
        """中国語簡体字日付フォーマットのテスト"""
        mock_session_state['language'] = 'zh-cn'
        
        i18n = I18nHelper()
        formatted_date = i18n.format_date(self.test_date)
        self.assertEqual(formatted_date, "2025年07月25日")
    
    @patch('streamlit.session_state', new_callable=lambda: {})
    def test_chinese_traditional_date_format(self, mock_session_state):
        """中国語繁体字日付フォーマットのテスト"""
        mock_session_state['language'] = 'zh-tw'
        
        i18n = I18nHelper()
        formatted_date = i18n.format_date(self.test_date)
        self.assertEqual(formatted_date, "2025年07月25日")
    
    @patch('streamlit.session_state', new_callable=lambda: {})
    def test_english_date_format(self, mock_session_state):
        """英語日付フォーマットのテスト"""
        mock_session_state['language'] = 'en'
        
        i18n = I18nHelper()
        formatted_date = i18n.format_date(self.test_date)
        self.assertEqual(formatted_date, "July 25, 2025")


class TestPlaceholderReplacement(unittest.TestCase):
    
    @patch('streamlit.session_state', new_callable=lambda: {})
    def test_korean_placeholder_replacement(self, mock_session_state):
        """韓国語プレースホルダー置換のテスト"""
        mock_session_state['language'] = 'ko'
        
        i18n = I18nHelper()
        result = i18n.t('update_count', count=5)
        self.assertEqual(result, "업데이트가 5개 있습니다.")
    
    @patch('streamlit.session_state', new_callable=lambda: {})
    def test_chinese_simplified_placeholder_replacement(self, mock_session_state):
        """中国語簡体字プレースホルダー置換のテスト"""
        mock_session_state['language'] = 'zh-cn'
        
        i18n = I18nHelper()
        result = i18n.t('update_count', count=5)
        self.assertEqual(result, "有 5 个更新。")
    
    @patch('streamlit.session_state', new_callable=lambda: {})
    def test_chinese_traditional_placeholder_replacement(self, mock_session_state):
        """中国語繁体字プレースホルダー置換のテスト"""
        mock_session_state['language'] = 'zh-tw'
        
        i18n = I18nHelper()
        result = i18n.t('update_count', count=5)
        self.assertEqual(result, "有 5 個更新。")
    
    @patch('streamlit.session_state', new_callable=lambda: {})
    def test_english_placeholder_replacement(self, mock_session_state):
        """英語プレースホルダー置換のテスト"""
        mock_session_state['language'] = 'en'
        
        i18n = I18nHelper()
        result = i18n.t('update_count', count=5)
        self.assertEqual(result, "There are 5 updates.")


if __name__ == '__main__':
    unittest.main()