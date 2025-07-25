import json
import os
import streamlit as st
import locale

# 言語設定
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

# Azure OpenAI システムプロンプト（言語別）
SYSTEM_PROMPTS = {
    "ja": ("渡されたデータに含まれている Azure のアップデート情報を日本語で 3 行程度で要約してください。" +
           "各提供する地域のリージョンについては、翻訳せずに英語表記のままにしてください。" +
           "リンク用のURLやマークダウンは含まず、プレーンテキストで出力してください。"),
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
    "id": ("Harap meringkas informasi pembaruan Azure yang terdapat dalam data yang diberikan dalam bahasa Indonesia sekitar 3 baris." +
           "Untuk wilayah di setiap area yang disediakan, jangan diterjemahkan dan tetap gunakan notasi bahasa Inggris." +
           "Jangan menyertakan URL untuk tautan atau markdown dan output dalam teks biasa."),
    "hi": ("कृपया प्रदान किए गए डेटा में निहित Azure अपडेट जानकारी को हिंदी में लगभग 3 पंक्तियों में सारांशित करें।" +
           "प्रत्येक प्रदान किए गए क्षेत्र के क्षेत्रों के लिए, अनुवाद न करें और अंग्रेजी संकेतन को वैसा ही रखें।" +
           "लिंक के लिए URL या markdown शामिल न करें और सादे पाठ में आउटपुट करें।")
}

# 日付フォーマット（言語別）
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
        """翻訳ファイルを読み込み"""
        translations_path = os.path.join(os.path.dirname(__file__), 'locales', 'translations.json')
        with open(translations_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def get_current_language(self):
        """現在選択されている言語を取得"""
        if 'language' not in st.session_state:
            # 初回アクセス時はブラウザ言語を検出
            detected_lang = self._detect_browser_language()
            st.session_state.language = detected_lang
        return st.session_state['language']
    
    def _detect_browser_language(self):
        """ブラウザ言語検出のフォールバック"""
        # セッション状態から検出された言語を取得
        if 'detected_browser_language' in st.session_state:
            return st.session_state.detected_browser_language
        
        # フォールバック: システムロケールから推測
        detected = self._detect_system_locale()
        st.session_state.detected_browser_language = detected
        return detected
    
    def _detect_system_locale(self):
        """システムロケールから言語を推測"""
        try:
            system_locale = locale.getdefaultlocale()[0]
            if system_locale:
                # JavaScript mapping に基づく言語検出
                if system_locale.startswith('ja'):
                    return 'ja'
                elif system_locale.startswith('en'):
                    return 'en'
                elif system_locale.startswith('ko'):
                    return 'ko'
                elif system_locale.startswith('zh_CN'):
                    return 'zh-cn'
                elif system_locale.startswith('zh_TW') or system_locale.startswith('zh_HK'):
                    return 'zh-tw'
                elif system_locale == 'zh':  # 汎用中国語は簡体字にマップ
                    return 'zh-cn'
                elif system_locale.startswith('th'):
                    return 'th'
                elif system_locale.startswith('vi'):
                    return 'vi'
                elif system_locale.startswith('id'):
                    return 'id'
                elif system_locale.startswith('hi'):
                    return 'hi'
                else:
                    return 'en'
        except:
            pass
        return 'en'  # デフォルト
    
    def set_language(self, language_code):
        """言語を設定"""
        if language_code in LANGUAGES:
            st.session_state.language = language_code
    
    def t(self, key, **kwargs):
        """翻訳テキストを取得（プレースホルダー対応）"""
        current_lang = self.get_current_language()
        
        if current_lang in self.translations and key in self.translations[current_lang]:
            text = self.translations[current_lang][key]
            # プレースホルダーを置換
            if kwargs:
                text = text.format(**kwargs)
            return text
        
        # フォールバック: 日本語
        if key in self.translations['ja']:
            text = self.translations['ja'][key]
            if kwargs:
                text = text.format(**kwargs)
            return text
        
        # キーが見つからない場合
        return f"[Missing: {key}]"
    
    def get_system_prompt(self):
        """現在の言語に応じたシステムプロンプトを取得"""
        current_lang = self.get_current_language()
        return SYSTEM_PROMPTS.get(current_lang, SYSTEM_PROMPTS['ja'])
    
    def format_date(self, date_obj):
        """現在の言語に応じた日付フォーマットを適用"""
        current_lang = self.get_current_language()
        date_format = DATE_FORMATS.get(current_lang, DATE_FORMATS['ja'])
        return date_obj.strftime(date_format)
    
    def language_selector(self):
        """言語選択ウィジェットを表示"""
        current_lang = self.get_current_language()
        
        # 現在の言語のインデックスを取得
        lang_codes = list(LANGUAGES.keys())
        current_index = lang_codes.index(current_lang) if current_lang in lang_codes else 0
        
        # ブラウザ言語検出の情報を表示
        if 'language_auto_detected' not in st.session_state:
            st.session_state.language_auto_detected = True
            if current_lang != 'en':  # デフォルト以外が検出された場合のみ表示
                st.info(f"🌐 システム設定に基づいて{LANGUAGES.get(current_lang, current_lang)}が選択されました")
        
        # セレクトボックスを表示
        selected_lang = st.selectbox(
            "Language / 言語",
            options=lang_codes,
            format_func=lambda x: LANGUAGES[x],
            index=current_index,
            key="language_selector"
        )
        
        # 言語が変更された場合
        if selected_lang != current_lang:
            self.set_language(selected_lang)
            st.rerun()

# グローバルインスタンス
i18n = I18nHelper()