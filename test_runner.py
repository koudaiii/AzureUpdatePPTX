import unittest
import sys
import os
import traceback


def run_tests():
    """テストを実行する"""
    try:
        # 現在の作業ディレクトリを表示
        current_dir = os.getcwd()
        print(f"現在の作業ディレクトリ: {current_dir}")

        # スクリプトのディレクトリに移動
        test_dir = os.path.dirname(os.path.abspath(__file__))
        os.chdir(test_dir)
        print(f"テストディレクトリに移動: {test_dir}")

        # 利用可能なPythonモジュールを確認
        print("ディレクトリ内のPythonファイル:")
        for file in os.listdir(test_dir):
            if file.endswith('.py'):
                print(f" - {file}")

        # テストを検索して実行
        print("テストの検索と実行を開始...")
        suite = unittest.defaultTestLoader.discover('.', pattern='test_*.py')
        result = unittest.TextTestRunner(verbosity=2).run(suite)

        if result.wasSuccessful():
            print("すべてのテストが成功しました")
            return 0
        else:
            print(f"テストに失敗しました: {len(result.failures)} failures, {len(result.errors)} errors")
            return 1
    except Exception as e:
        print(f"テスト実行中に予期せぬエラーが発生しました: {e}")
        traceback.print_exc()
        return 1


if __name__ == '__main__':
    sys.exit(run_tests())
