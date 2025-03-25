import os
import sys
import shutil
from bs4 import BeautifulSoup
import logging
import textwrap

# ロギング設定
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


def find_streamlit_index_path(custom_path=None):
    """Streamlitのindex.htmlファイルのパスを探す

    Args:
        custom_path: 優先的に確認する任意のパス

    Returns:
        見つかったindex.htmlのパス、見つからない場合はNone
    """
    # 任意のパスが指定された場合、最初にそれを確認
    if custom_path and os.path.exists(custom_path):
        logging.info(f"指定されたパスでindex.htmlを発見: {custom_path}")
        return custom_path
    elif custom_path and not os.path.exists(custom_path):
        logging.warning(f"指定されたパスにindex.htmlが見つかりません: {custom_path}")
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
    logging.error("Streamlitのindex.htmlファイルが見つかりません")
    return None


def create_backup(file_path):
    """指定されたファイルのバックアップを作成する"""
    backup_path = file_path + '.bak'

    if not os.path.exists(file_path):
        logging.error(f"エラー: ファイルが存在しません: {file_path}")
        return False

    if not os.path.exists(backup_path):
        try:
            shutil.copyfile(file_path, backup_path)
            logging.info(f"バックアップを作成しました: {backup_path}")
        except Exception as e:
            logging.error(f"バックアップの作成に失敗しました: {e}")
            return False
    else:
        logging.info(f"バックアップは既に存在します: {backup_path}")

    return True


def get_meta_tags():
    """追加するメタタグのリストを返す"""
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
        {'property': 'twitter:domain', 'content': 'azure.koudaiii.com'},
        {'property': 'twitter:url', 'content': 'https://azure.koudaiii.com'},
        {'name': 'twitter:image', 'content': 'https://koudaiii.com/azure_update_summary.png'},
        {'name': 'twitter:title', 'content': 'Azure Updates Summary'},
        {'name': 'twitter:card', 'content': 'summary_large_image'},
        {'name': 'twitter:site', 'content': '@koudaiii'},
        {'name': 'twitter:creator', 'content': '@koudaiii'}
    ]


def get_banner_style():
    """ヘッダーバナーのスタイルを返す"""
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


def modify_html(file_path):
    """HTMLファイルにメタタグとヘッダーバナーを追加する"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            html_content = f.read()

        soup = BeautifulSoup(html_content, 'html.parser')

        # メタタグを追加
        for tag in get_meta_tags():
            meta = soup.new_tag('meta')
            for key, value in tag.items():
                meta[key] = value
            soup.head.append(meta)

        # スタイルを追加
        style_tag = soup.new_tag('style')
        style_tag.string = get_banner_style()
        soup.head.append(style_tag)

        # ヘッダーバナーを追加
        banner = soup.new_tag('div', attrs={'class': 'header-banner'})
        banner.string = "Public Preview"
        soup.body.insert(0, banner)

        # 変更を保存
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(str(soup))

        logging.info("メタタグとヘッダーバナーが追加されました")
        return True
    except Exception as e:
        logging.error(f"HTMLファイルの修正に失敗しました: {e}")
        return False


def main(custom_path=None):
    """メイン関数

    Args:
        custom_path: 任意のStreamlitのindex.htmlパス
    """
    # Streamlitのindex.htmlを見つける
    streamlit_path = find_streamlit_index_path(custom_path)
    if not streamlit_path:
        logging.error("Streamlitのindex.htmlが見つかりませんでした")
        sys.exit(1)

    # バックアップを作成
    if not create_backup(streamlit_path):
        logging.error("バックアップの作成に失敗しました")
        sys.exit(1)

    # HTMLを修正
    if not modify_html(streamlit_path):
        logging.error("HTMLの修正に失敗しました")
        sys.exit(1)

    print("Streamlitのindex.htmlファイルにメタタグとヘッダーバナーが追加されました。")


if __name__ == "__main__":
    # コマンドライン引数からカスタムパスを取得する場合はここで処理
    import argparse
    parser = argparse.ArgumentParser(description='Streamlit HTMLにメタタグとヘッダーバナーを追加します')
    parser.add_argument('--path', help='Streamlit index.htmlのカスタムパス')
    args = parser.parse_args()

    main(args.path)
