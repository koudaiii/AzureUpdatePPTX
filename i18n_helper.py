"""
Internationalization (i18n) helper module for Azure Update PPTX application.

This module provides language detection, translation management, and localization
support for multiple languages including Japanese, English, Korean, Chinese,
Thai, Vietnamese, Indonesian, and Hindi.
"""

import json
import os
from datetime import datetime
from typing import Dict, Any

import streamlit as st


# Supported languages configuration
LANGUAGES: Dict[str, str] = {
    "ja": "日本語",
    "en": "English",
    "ko": "한국어",
    "zh-cn": "中文(简体)",
    "zh-tw": "中文(繁體)",
    "th": "ไทย",
    "vi": "Tiếng Việt",
    "id": "Bahasa Indonesia",
    "hi": "हिन्दी"
}


# Azure OpenAI system prompts for each language
SYSTEM_PROMPTS: Dict[str, str] = {
    "ja": (
        "渡されたデータに含まれている Azure のアップデート情報を日本語で 3 行程度で要約してください。"
        "各提供する地域のリージョンについては、翻訳せずに英語表記のままにしてください。"
        "リンク用のURLやマークダウンは含まず、プレーンテキストで出力してください。"
    ),
    "en": (
        "Please summarize the Azure update information contained in the provided data in about 3 lines in English."
        "For regions in each provided area, keep them in English notation without translation."
        "Output in plain text without including URLs for links or markdown."
    ),
    "ko": (
        "제공된 데이터에 포함된 Azure 업데이트 정보를 한국어로 3줄 정도로 요약해 주세요."
        "각 제공 지역의 리전에 대해서는 번역하지 말고 영어 표기 그대로 두세요."
        "링크용 URL이나 마크다운은 포함하지 말고 일반 텍스트로 출력해 주세요."
    ),
    "zh-cn": (
        "请用中文(简体)将提供数据中包含的 Azure 更新信息用大约 3 行总结。"
        "对于各提供地区的区域，请不要翻译，保持英文表示。"
        "不要包含链接用的URL或markdown，请用纯文本输出。"
    ),
    "zh-tw": (
        "請用中文(繁體)將提供數據中包含的 Azure 更新資訊用大約 3 行總結。"
        "對於各提供地區的區域，請不要翻譯，保持英文表示。"
        "不要包含連結用的URL或markdown，請用純文字輸出。"
    ),
    "th": (
        "โปรดสรุปข้อมูลอัปเดต Azure ที่มีอยู่ในข้อมูลที่ให้มาเป็นภาษาไทยประมาณ 3 บรรทัด"
        "สำหรับภูมิภาคในแต่ละพื้นที่ที่ให้บริการ โปรดไม่ต้องแปลและให้คงไว้เป็นภาษาอังกฤษ"
        "อย่าใส่ URL สำหรับลิงก์หรือ markdown และให้แสดงผลเป็นข้อความธรรมดา"
    ),
    "vi": (
        "Vui lòng tóm tắt thông tin cập nhật Azure có trong dữ liệu được cung cấp bằng tiếng Việt trong khoảng 3 dòng."
        "Đối với các khu vực trong từng khu vực được cung cấp, vui lòng không dịch và giữ nguyên ký hiệu tiếng Anh."
        "Không bao gồm URL cho liên kết hoặc markdown và xuất ra dưới dạng văn bản thuần túy."
    ),
    "id": (
        "Harap meringkas informasi pembaruan Azure yang terdapat dalam data yang diberikan "
        "dalam bahasa Indonesia sekitar 3 baris."
        "Untuk wilayah di setiap area yang disediakan, jangan diterjemahkan dan tetap gunakan notasi bahasa Inggris."
        "Jangan menyertakan URL untuk tautan atau markdown dan output dalam teks biasa."
    ),
    "hi": (
        "कृपया प्रदान किए गए डेटा में निहित Azure अपडेट जानकारी को हिंदी में लगभग 3 पंक्तियों में सारांशित करें।"
        "प्रत्येक प्रदान किए गए क्षेत्र के क्षेत्रों के लिए, अनुवाद न करें और अंग्रेजी संकेतन को वैसा ही रखें।"
        "लिंक के लिए URL या markdown शामिल न करें और सादे पाठ में आउटपुट करें।"
    )
}


# Date format patterns for each language
DATE_FORMATS: Dict[str, str] = {
    "ja": "%Y年%m月%d日",
    "en": "%B %d, %Y",
    "ko": "%Y년 %m월 %d일",
    "zh-cn": "%Y年%m月%d日",
    "zh-tw": "%Y年%m月%d日",
    "th": "%d %B %Y",
    "vi": "ngày %d tháng %m năm %Y",
    "id": "%d %B %Y",
    "hi": "%d %B %Y"
}


class I18nHelper:
    """
    Helper class for internationalization support.

    Provides methods for language detection, translation management,
    and localization of dates and system prompts.
    """

    def __init__(self):
        """Initialize the I18nHelper with translation data."""
        self.translations = self._load_translations()

    def _load_translations(self) -> Dict[str, Dict[str, str]]:
        """
        Load translation files from the locales directory.

        Returns:
            Dictionary containing translations for all supported languages.
            Falls back to minimal translations if loading fails.
        """
        translations_path = os.path.join(
            os.path.dirname(__file__), 'locales', 'translations.json'
        )

        try:
            with open(translations_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError) as e:
            st.error(f"Failed to load translation files: {e}")
            return {
                "ja": {"main_title": "Azure Updates Summary", "button_text": "データを取得"},
                "en": {"main_title": "Azure Updates Summary", "button_text": "Get Data"}
            }

    def get_current_language(self) -> str:
        """
        Get the currently selected language.

        Returns:
            Current language code (e.g., 'ja', 'en').
        """
        if 'language' not in st.session_state:
            # Detect browser language on first access
            detected_lang = self._detect_browser_language()
            st.session_state.language = detected_lang
        return st.session_state['language']

    def set_language(self, language_code: str) -> None:
        """
        Set the current language.

        Args:
            language_code: Language code to set (must be in LANGUAGES).
        """
        if not isinstance(language_code, str) or language_code not in LANGUAGES:
            st.error(
                self.t("invalid_language_code", language_code=language_code)
            )
            st.session_state.language = 'en'
            return

        st.session_state.language = language_code

    def t(self, key: str, **kwargs: Any) -> str:
        """
        Get translated text for the given key.

        Args:
            key: Translation key to look up.
            **kwargs: Placeholder values for string formatting.

        Returns:
            Translated text with placeholders replaced, or error message if not found.
        """
        current_lang = self.get_current_language()

        # Try current language first
        if (current_lang in self.translations and
                key in self.translations[current_lang]):
            text = self.translations[current_lang][key]
            if kwargs:
                text = text.format(**kwargs)
            return text

        # Fallback to Japanese
        if 'ja' in self.translations and key in self.translations['ja']:
            text = self.translations['ja'][key]
            if kwargs:
                text = text.format(**kwargs)
            return text

        # Key not found
        return f"[Missing: {key}]"

    def get_system_prompt(self) -> str:
        """
        Get the Azure OpenAI system prompt for the current language.

        Returns:
            System prompt string in the current language.
        """
        current_lang = self.get_current_language()
        return SYSTEM_PROMPTS.get(current_lang, SYSTEM_PROMPTS['ja'])

    def format_date(self, date_obj: datetime) -> str:
        """
        Format a date object according to the current language's format.

        Args:
            date_obj: datetime object to format.

        Returns:
            Formatted date string.
        """
        current_lang = self.get_current_language()
        date_format = DATE_FORMATS.get(current_lang, DATE_FORMATS['ja'])
        return date_obj.strftime(date_format)

    def language_selector(self) -> None:
        """
        Display the language selection widget in Streamlit.

        Handles browser language detection and user language selection.
        """
        self._process_language_query_param()
        current_lang = self.get_current_language()

        # Get index of current language
        lang_codes = list(LANGUAGES.keys())
        current_index = (
            lang_codes.index(current_lang)
            if current_lang in lang_codes else 0
        )

        # Display browser language detection info
        if 'language_auto_detected' not in st.session_state:
            st.session_state.language_auto_detected = True
            # Display only when non-default is detected
            if current_lang != 'en':
                lang_name = LANGUAGES.get(current_lang, current_lang)
                st.info(
                    f"🌐 {lang_name} was selected based on system settings"
                )

        # Display select box with on_change callback
        def on_language_change():
            selected_lang = st.session_state.language_selector
            if selected_lang != st.session_state.get('language', 'en'):
                st.session_state.language = selected_lang

        st.selectbox(
            "Language / 言語",
            options=lang_codes,
            format_func=lambda x: LANGUAGES[x],
            index=current_index,
            key="language_selector",
            on_change=on_language_change
        )

    def _detect_browser_language(self) -> str:
        """
        Detect the browser language.

        Returns:
            Detected language code, defaults to 'en' if detection fails.
        """
        # Get detected language from session state
        if 'detected_browser_language' in st.session_state:
            return st.session_state.detected_browser_language

        # Check if browser language was detected via JavaScript
        if 'browser_detected_lang' in st.session_state:
            detected = st.session_state.browser_detected_lang
            st.session_state.detected_browser_language = detected
            return detected

        # Default to English if no browser detection
        detected = 'en'
        st.session_state.detected_browser_language = detected
        return detected

    def _process_language_query_param(self) -> None:
        """
        Handle browser language detection via query parameters.

        Checks for browser_lang in query parameters and sets the language
        accordingly.
        """
        # Skip if already processed
        if 'browser_lang_processed' in st.session_state:
            return

        # Check for browser language in query parameters
        query_params = st.query_params
        if 'browser_lang' in query_params:
            browser_lang = query_params['browser_lang']
            if browser_lang in LANGUAGES:
                # Set the detected language in session state
                st.session_state.language = browser_lang
                st.session_state.browser_detected_lang = browser_lang
                st.session_state.detected_browser_language = browser_lang
                st.session_state.language_auto_detected = True
                # Mark as processed and clear parameter
                st.session_state.browser_lang_processed = True
                st.query_params.clear()
            else:
                # Clear invalid parameter
                st.query_params.clear()
                st.session_state.browser_lang_processed = True
        else:
            st.session_state.browser_lang_processed = True


# Global instance for easy access
i18n = I18nHelper()


def initialize_language_from_query_params() -> None:
    """
    Initialize language from query parameters before st.set_page_config.

    This function should be called at the very beginning of the main script
    to ensure language is set before any UI rendering.
    """
    query_params = st.query_params
    if 'browser_lang' in query_params:
        browser_lang = query_params['browser_lang']
        if browser_lang in LANGUAGES:
            # Initialize language in session state before any UI rendering
            st.session_state.language = browser_lang
            st.session_state.browser_detected_lang = browser_lang
            st.session_state.detected_browser_language = browser_lang
            st.session_state.language_auto_detected = True
