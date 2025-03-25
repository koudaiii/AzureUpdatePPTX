import os
import unittest
from unittest import mock
import tempfile
import shutil
from bs4 import BeautifulSoup
import add_meta_tags_and_header_banner

possible_paths = [
    "/app/streamlit/frontend/build/index.html",
    "/usr/local/lib/python3.9/site-packages/streamlit/static/index.html",
    "/usr/local/lib/python3.8/dist-packages/streamlit/static/index.html",
    "/usr/local/lib/python3.12/site-packages/streamlit/static/index.html"
]


class TestAddMetaTagsAndHeaderBanner(unittest.TestCase):

    def setUp(self):
        """テスト前の準備"""
        # テスト用の一時ディレクトリを作成
        self.test_dir = tempfile.mkdtemp()

        # テスト用のHTMLファイルを作成
        self.test_html = os.path.join(self.test_dir, 'test_index.html')
        with open(self.test_html, 'w') as f:
            f.write("""
            <!DOCTYPE html>
            <html>
            <head><title>Test Page</title></head>
            <body>Test Content</body>
            </html>
            """)

        self.custom_index_path = os.path.join(self.test_dir, 'custom_index.html')
        with open(self.custom_index_path, 'w') as f:
            f.write("""
            <!DOCTYPE html>
            <html>
            <head><title>Custom Page</title></head>
            <body>Custom Content</body>
            </html>
            """)

    def tearDown(self):
        """テスト後のクリーンアップ"""
        # テスト用ディレクトリを削除
        shutil.rmtree(self.test_dir)

    def test_find_streamlit_index_path(self):
        """find_streamlit_index_path関数のテスト - カスタムパスとデフォルトパスの両方をテスト"""

        # カスタムパスのテスト - 存在するパス
        custom_path = self.test_html
        self.assertEqual(add_meta_tags_and_header_banner.find_streamlit_index_path(custom_path), self.test_html)

        # カスタムパスのテスト - 存在しないパス
        custom_path = "/non-existent/path/index.html"
        self.assertNotEqual(add_meta_tags_and_header_banner.find_streamlit_index_path(custom_path), custom_path)

        # 特定のパスが存在する場合のテスト
        for test_path in possible_paths:
            with mock.patch('os.path.exists', side_effect=lambda x: x == test_path):
                found_path = add_meta_tags_and_header_banner.find_streamlit_index_path()
                self.assertEqual(found_path, test_path)

    def test_create_backup(self):
        """create_backup関数のテスト"""

        # バックアップを作成するファイルのパス
        file_path = os.path.join(self.test_dir, 'test_index.html')
        add_meta_tags_and_header_banner.create_backup(file_path)
        self.assertTrue(os.path.exists(file_path + '.bak'))

    def test_get_meta_tags(self):
        """get_meta_tags関数のテスト"""
        tags = add_meta_tags_and_header_banner.get_meta_tags()

        # タグがリストであることを確認
        self.assertIsInstance(tags, list)

        # タグが辞書であることを確認
        for tag in tags:
            self.assertIsInstance(tag, dict)

        # 必要なメタタグが含まれていることを確認
        self.assertIn({'name': 'description', 'content': 'Azure Update PPTXを使用してAzureアップデート情報を要約します。'}, tags)
        self.assertIn({'property': 'og:title', 'content': 'Azure Update PPTX'}, tags)

    def test_get_banner_style(self):
        """get_banner_style関数のテスト"""

        style = add_meta_tags_and_header_banner.get_banner_style()

        # スタイルが文字列であることを確認
        self.assertIsInstance(style, str)

        # 必要なスタイル要素が含まれていることを確認
        self.assertIn('.header-banner', style)
        self.assertIn('position: fixed', style)

    def test_modify_html(self):
        """modify_html関数のテスト"""

        # カスタムパスを使用してテスト
        self.assertTrue(add_meta_tags_and_header_banner.modify_html(self.custom_index_path))

        # 修正されたHTMLを確認
        with open(self.custom_index_path, 'r') as f:
            modified_html = f.read()

        soup = BeautifulSoup(modified_html, 'html.parser')

        # メタタグが追加されていることを確認
        meta_tags = soup.find_all('meta')
        self.assertTrue(len(meta_tags) > 0)

        # スタイルタグが追加されていることを確認
        style_tag = soup.find('style')
        self.assertIsNotNone(style_tag)
        self.assertIn('.header-banner', style_tag.text)

        # ヘッダーバナーが追加されていることを確認
        banner = soup.find('div', {'class': 'header-banner'})
        self.assertIsNotNone(banner)
        self.assertEqual(banner.text, "Public Preview")

        # 存在しないファイルでテスト
        non_existent_file_path = os.path.join(self.test_dir, 'non_existent.html')
        self.assertFalse(add_meta_tags_and_header_banner.modify_html(non_existent_file_path))


if __name__ == '__main__':
    unittest.main()
