// ブラウザの言語設定を検出してStreamlitに送信
function detectBrowserLanguage() {
    // ブラウザの言語設定を取得
    let browserLang = navigator.language || navigator.userLanguage;
    
    // 言語コードをマッピング
    const langMapping = {
        'ja': 'ja',
        'ja-JP': 'ja',
        'en': 'en',
        'en-US': 'en', 
        'en-GB': 'en',
        'ko': 'ko',
        'ko-KR': 'ko',
        'zh': 'zh-cn',
        'zh-CN': 'zh-cn',
        'zh-TW': 'zh-tw',
        'zh-HK': 'zh-tw',
        'th': 'th',
        'th-TH': 'th',
        'vi': 'vi',
        'vi-VN': 'vi',
        'id': 'id',
        'id-ID': 'id',
        'hi': 'hi',
        'hi-IN': 'hi'
    };
    
    // 対応する言語コードを取得（デフォルトは英語）
    let detectedLang = langMapping[browserLang] || 'en';
    
    // 言語の優先順位を考慮（ブラウザが複数の言語を返す場合）
    if (navigator.languages && navigator.languages.length > 0) {
        for (let lang of navigator.languages) {
            if (langMapping[lang]) {
                detectedLang = langMapping[lang];
                break;
            }
        }
    }
    
    // Streamlitのセッション状態に言語を設定
    if (window.parent && window.parent.postMessage) {
        window.parent.postMessage({
            type: 'SET_BROWSER_LANGUAGE',
            language: detectedLang
        }, window.location.origin);
    }
    
    return detectedLang;
}

// ページ読み込み時に実行
document.addEventListener('DOMContentLoaded', detectBrowserLanguage);

// Streamlitコンポーネントとしても使用可能
if (typeof Streamlit !== 'undefined') {
    Streamlit.setComponentReady();
    Streamlit.setComponentValue(detectBrowserLanguage());
}
