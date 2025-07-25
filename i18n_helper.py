import json
import os
import streamlit as st
import locale

# Language settings
LANGUAGES = {
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

# Azure OpenAI system prompts (by language)
SYSTEM_PROMPTS = {
  "ja": ("渡されたデータに含まれている Azure のアップデート情報を日本語で 3 行程度で要約してください。" +
         "各提供する地域のリージョンについては、翻訳せずに英語表記のままにしてください。" +
         "リンク用のURLやマークダウンは含まず、"
         "プレーンテキストで出力してください。"),
  "en": ("Please summarize the Azure update information contained in the provided data in about 3 lines in English." +
         "For regions in each provided area, keep them in English notation without translation." +
         "Output in plain text without including URLs for links or markdown."),
  "ko": ("제공된 데이터에 포함된 Azure 업데이트 정보를 한국어로 3줄 정도로 요약해 주세요." +
         "각 제공 지역의 리전에 대해서는 번역하지 말고 영어 표기 그대로 두세요." +
         "링크용 URL이나 마크다운은 포함하지 말고 일반 텍스트로 출력해 주세요."),
  "zh-cn": ("请用中文(简体)将提供数据中包含的 Azure 更新信息用大约 3 行总结。" +
            "对于各提供地区的区域，请不要翻译，保持英文表示。" +
            "不要包含链接用的URL或markdown，请用纯文本输出。"),
  "zh-tw": ("請用中文(繁體)將提供數據中包含的 Azure 更新資訊用大約 3 行總結。" +
            "對於各提供地區的區域，請不要翻譯，保持英文表示。" +
            "不要包含連結用的URL或markdown，請用純文字輸出。"),
  "th": ("โปรดสรุปข้อมูลอัปเดต Azure ที่มีอยู่ในข้อมูลที่ให้มาเป็นภาษาไทยประมาณ 3 บรรทัด" +
         "สำหรับภูมิภาคในแต่ละพื้นที่ที่ให้บริการ โปรดไม่ต้องแปลและให้คงไว้เป็นภาษาอังกฤษ" +
         "อย่าใส่ URL สำหรับลิงก์หรือ markdown และให้แสดงผลเป็นข้อความธรรมดา"),
  "vi": ("Vui lòng tóm tắt thông tin cập nhật Azure có trong dữ liệu được cung cấp bằng tiếng Việt trong khoảng 3 dòng." +
         "Đối với các khu vực trong từng khu vực được cung cấp, vui lòng không dịch và giữ nguyên ký hiệu tiếng Anh." +
         "Không bao gồm URL cho liên kết hoặc markdown và xuất ra dưới dạng văn bản thuần túy."),
  "id": ("Harap meringkas informasi pembaruan Azure yang terdapat dalam data yang diberikan " +
         "dalam bahasa Indonesia sekitar 3 baris." +
         "Untuk wilayah di setiap area yang disediakan, jangan diterjemahkan dan tetap gunakan notasi bahasa Inggris." +
         "Jangan menyertakan URL untuk tautan atau markdown dan output dalam teks biasa."),
  "hi": ("कृपया प्रदान किए गए डेटा में निहित Azure अपडेट जानकारी को हिंदी में लगभग 3 पंक्तियों में सारांशित करें।" +
         "प्रत्येक प्रदान किए गए क्षेत्र के क्षेत्रों के लिए, अनुवाद न करें और अंग्रेजी संकेतन को वैसा ही रखें।" +
         "लिंक के लिए URL या markdown शामिल न करें और सादे पाठ में आउटपुट करें।")
}

# Date formats (by language)
DATE_FORMATS = {
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

    def __init__(self):
        self.translations = self._load_translations()

    def _load_translations(self):
        """Load translation files"""
        translations_path = os.path.join(
            os.path.dirname(__file__), 'locales', 'translations.json'
        )
        try:
            with open(translations_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError) as e:
            st.error(f"Failed to load translation files: {e}")
            # Fallback: return minimal empty translations
            return {"ja": {}, "en": {}}  # Minimal fallback

    def get_current_language(self):
        """Get currently selected language"""
        if 'language' not in st.session_state:
            # Detect browser language on first access
            detected_lang = self._detect_browser_language()
            st.session_state.language = detected_lang
            # Debug logging
            print(f"[DEBUG] Initial language detection: {detected_lang}")
        return st.session_state['language']

    def _detect_browser_language(self):
        """Browser language detection fallback"""
        # Get detected language from session state
        if 'detected_browser_language' in st.session_state:
            print(f"[DEBUG] Using cached detected_browser_language: {st.session_state.detected_browser_language}")
            return st.session_state.detected_browser_language

        # Check if browser language was detected via JavaScript
        if 'browser_detected_lang' in st.session_state:
            detected = st.session_state.browser_detected_lang
            st.session_state.detected_browser_language = detected
            print(f"[DEBUG] Using browser_detected_lang: {detected}")
            return detected

        detected = self._detect_system_locale()
        st.session_state.detected_browser_language = detected
        return detected

    def _detect_system_locale(self):
        """Infer language from system locale"""
        try:
            system_locale = locale.getdefaultlocale()[0]
            if not system_locale:
                return 'en'

            # Language detection based on JavaScript mapping
            locale_map = {
                'ja': 'ja', 'en': 'en', 'ko': 'ko',
                'zh_CN': 'zh-cn', 'zh_TW': 'zh-tw', 'zh_HK': 'zh-tw',
                'zh': 'zh-cn', 'th': 'th', 'vi': 'vi',
                'id': 'id', 'hi': 'hi'
            }

            # Check exact match first
            if system_locale in locale_map:
                return locale_map[system_locale]

            # Check prefix matches
            for locale_prefix, lang_code in locale_map.items():
                if system_locale.startswith(locale_prefix + '_'):
                    return lang_code

            # Check if it's an English locale variant
            if system_locale.startswith('en_'):
                return 'en'

            return 'en'
        except (OSError, AttributeError):
            pass
        return 'en'  # Default

    def set_language(self, language_code):
        """Set language"""
        if not isinstance(language_code, str) or language_code not in LANGUAGES:
            st.error(f"Invalid language code: {language_code}, "
                     "Setting to default (English).")
            # Default to English if invalid and return
            st.session_state.language = 'en'
            return
        # Set the language if valid
        st.session_state.language = language_code

    def t(self, key, **kwargs):
        """Get translated text (with placeholder support)"""
        current_lang = self.get_current_language()

        if (current_lang in self.translations and
                key in self.translations[current_lang]):
            text = self.translations[current_lang][key]
            # Replace placeholders
            if kwargs:
                text = text.format(**kwargs)
            return text

        # Fallback: Japanese
        if key in self.translations['ja']:
            text = self.translations['ja'][key]
            if kwargs:
                text = text.format(**kwargs)
            return text

        # If key is not found
        return f"[Missing: {key}]"

    def get_system_prompt(self):
        """Get system prompt according to current language"""
        current_lang = self.get_current_language()
        return SYSTEM_PROMPTS.get(current_lang, SYSTEM_PROMPTS['ja'])

    def format_date(self, date_obj):
        """Apply date format according to current language"""
        current_lang = self.get_current_language()
        date_format = DATE_FORMATS.get(current_lang, DATE_FORMATS['ja'])
        return date_obj.strftime(date_format)

    def language_selector(self):
        """Display language selection widget"""
        # Inject JavaScript for browser language detection
        self._inject_language_detector()
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
                st.info(f"🌐 {lang_name} was selected based on "
                        "system settings")

        # Display select box
        selected_lang = st.selectbox(
            "Language / 言語",
            options=lang_codes,
            format_func=lambda x: LANGUAGES[x],
            index=current_index,
            key="language_selector"
        )

        # If language was changed
        if selected_lang != current_lang:
            self.set_language(selected_lang)
            st.rerun()

    def _inject_language_detector(self):
        """Inject JavaScript for browser language detection"""
        # Skip if already detected
        if 'browser_detected_lang' in st.session_state:
            return
        # Check for browser language in query parameters first
        query_params = st.query_params
        if 'browser_lang' in query_params:
            browser_lang = query_params['browser_lang']
            if browser_lang in LANGUAGES:
                # Set the detected language in session state
                if 'language' not in st.session_state or st.session_state.language != browser_lang:
                    st.session_state.language = browser_lang
                    st.session_state.browser_detected_lang = browser_lang
                    st.session_state.detected_browser_language = browser_lang
                    st.session_state.language_auto_detected = True
                    # Clear the query parameter and rerun to apply the language
                    st.query_params.clear()
                    st.rerun()
                else:
                    # Language already set correctly, just clear the parameter
                    st.query_params.clear()
            else:
                # Clear invalid parameter
                st.query_params.clear()


# Global instance
i18n = I18nHelper()
