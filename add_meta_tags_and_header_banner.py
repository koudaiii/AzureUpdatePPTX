import os
import sys
import shutil
from bs4 import BeautifulSoup
import logging
import textwrap

# Logging configuration
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


def find_streamlit_index_path(custom_path=None):
    """Find the path to Streamlit's index.html file

    Args:
        custom_path: Optional path to check with priority

    Returns:
        Path to the found index.html file, or None if not found
    """
    # If a custom path is specified, check it first
    if custom_path and os.path.exists(custom_path):
        logging.info(f"Found index.html at specified path: {custom_path}")
        return custom_path
    elif custom_path and not os.path.exists(custom_path):
        logging.warning(f"index.html not found at specified path: {custom_path}")
        return None

    possible_paths = [
        "/app/streamlit/frontend/build/index.html",
        "/usr/local/lib/python3.9/site-packages/streamlit/static/index.html",
        "/usr/local/lib/python3.8/dist-packages/streamlit/static/index.html",
        "/usr/local/lib/python3.12/site-packages/streamlit/static/index.html"
    ]

    for path in possible_paths:
        if os.path.exists(path):
            return path
    logging.error("Streamlit's index.html file not found")
    return None


def create_backup(file_path):
    """Create backup of the specified file"""
    backup_path = file_path + '.bak'

    if not os.path.exists(file_path):
        logging.error(f"Error: File does not exist: {file_path}")
        return False

    if not os.path.exists(backup_path):
        try:
            shutil.copyfile(file_path, backup_path)
            logging.info(f"Backup created: {backup_path}")
        except Exception as e:
            logging.error(f"Failed to create backup: {e}")
            return False
    else:
        logging.info(f"Backup already exists: {backup_path}")

    return True


def get_meta_tags():
    """Return list of meta tags to add"""
    return [
        # General SEO
        {'name': 'description', 'content': 'Azure Updates を要約して PPTX にまとめます。'},
        {'name': 'author', 'content': 'Kodai Sakabe'},
        {
            'name': 'keywords',
            'content': (
                'azure updates, azure, azure updates summary, '
                'azure updates generate pptx, updates, summary, powerpoint'
            )
        },
        # Open Graph
        {'property': 'og:title', 'content': 'Azure Updates Summary'},
        {'property': 'og:description', 'content': 'Azure Updates を要約して PPTX にまとめます。'},
        {'property': 'og:type', 'content': 'website'},
        {'property': 'og:url', 'content': 'https://azure.koudaiii.com'},
        {'property': 'og:image', 'content': 'https://koudaiii.com/azure_update_summary.png'},
        # Twitter
        {'name': 'twitter:description', 'content': 'Azure Updates を要約して PPTX にまとめます。'},
        {'name': 'twitter:domain', 'content': 'azure.koudaiii.com'},
        {'name': 'twitter:url', 'content': 'https://azure.koudaiii.com'},
        {'name': 'twitter:image', 'content': 'https://koudaiii.com/azure_update_summary.png'},
        {'name': 'twitter:title', 'content': 'Azure Updates Summary'},
        {'name': 'twitter:card', 'content': 'summary_large_image'},
        {'name': 'twitter:site', 'content': '@koudaiii'},
        {'name': 'twitter:creator', 'content': '@koudaiii'}
    ]


def get_banner_style():
    """Return header banner styles"""
    return textwrap.dedent("""
    .header-banner {
        color: black;
        text-align: center;
        font-size: 14px;
        position: fixed;
        top: 0;
        width: 100%;
        z-index: 999991;
    }
    """)


def get_language_detector_script():
    """Return language detector JavaScript code"""
    return textwrap.dedent("""
    // Detect browser language settings and send to Streamlit
    function detectBrowserLanguage() {
        // Get browser language settings
        let browserLang = navigator.language || navigator.userLanguage;
        console.log('Browser language detected:', browserLang);

        // Map language codes
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

        // Get corresponding language code (default is English)
        let detectedLang = langMapping[browserLang] || 'en';

        // Consider language priority (when browser returns multiple languages)
        if (navigator.languages && navigator.languages.length > 0) {
            for (let lang of navigator.languages) {
                if (langMapping[lang]) {
                    detectedLang = langMapping[lang];
                    break;
                }
            }
        }

        console.log('Mapped language:', detectedLang);

        // Add browser_lang parameter to URL and redirect
        const urlParams = new URLSearchParams(window.location.search);
        if (!urlParams.has('browser_lang') && !urlParams.has('lang_detected')) {
            urlParams.set('browser_lang', detectedLang);
            window.location.search = urlParams.toString();
        }

        return detectedLang;
    }

    // Execute on page load
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', detectBrowserLanguage);
    } else {
        detectBrowserLanguage();
    }
    """)


def modify_html(file_path):
    """Add meta tags, header banner, and language detector to HTML file"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            html_content = f.read()

        soup = BeautifulSoup(html_content, 'html.parser')

        # Add meta tags
        for tag in get_meta_tags():
            meta = soup.new_tag('meta')
            for key, value in tag.items():
                meta[key] = value
            soup.head.append(meta)

        # Add styles
        style_tag = soup.new_tag('style')
        style_tag.string = get_banner_style()
        soup.head.append(style_tag)

        # Add language detector script
        script_tag = soup.new_tag('script')
        script_tag.string = get_language_detector_script()
        soup.head.append(script_tag)

        # Add header banner
        banner = soup.new_tag('div', attrs={'class': 'header-banner'})
        banner.string = "Public Preview"
        soup.body.insert(0, banner)

        # Save changes
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(str(soup))

        logging.info("Meta tags, header banner, and language detector have been added")
        return True
    except Exception as e:
        logging.error(f"Failed to modify HTML file: {e}")
        return False


def main(custom_path=None):
    """Main function

    Args:
        custom_path: Optional Streamlit index.html path
    """
    # Find Streamlit's index.html
    streamlit_path = find_streamlit_index_path(custom_path)
    if not streamlit_path:
        logging.error("Streamlit's index.html was not found")
        sys.exit(1)

    # Create backup
    if not create_backup(streamlit_path):
        logging.error("Failed to create backup")
        sys.exit(1)

    # Modify HTML
    if not modify_html(streamlit_path):
        logging.error("Failed to modify HTML")
        sys.exit(1)

    print("Meta tags and header banner have been added to Streamlit's index.html file.")


if __name__ == "__main__":
    # Process custom path from command line arguments if needed
    import argparse
    parser = argparse.ArgumentParser(description='Add meta tags and header banner to Streamlit HTML')
    parser.add_argument('--path', help='Custom path to Streamlit index.html')
    args = parser.parse_args()

    main(args.path)
