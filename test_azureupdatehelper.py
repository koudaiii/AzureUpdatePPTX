import unittest
from unittest.mock import patch
import azureupdatehelper
import os


class TestAzureUpdateHelper(unittest.TestCase):
    def test_placeholder(self):
        self.assertTrue(True)


class TestEnvironmentCheck(unittest.TestCase):
    @patch.dict(os.environ, {
        "API_KEY": "test_api_key",
        "API_ENDPOINT": "https://example.com/openai/deployments/gpt-4o/chat/completions?api-version=2024-08-01-preview"
    }, clear=True)
    def test_environment_check_all_set(self):
        self.assertTrue(azureupdatehelper.environment_check())

    @patch.dict(os.environ, {
        "API_KEY": "",
        "API_ENDPOINT": "https://example.com/openai/deployments/gpt-4o/chat/completions?api-version=2024-08-01-preview"
    }, clear=True)
    def test_environment_check_missing_api_key(self):
        self.assertFalse(azureupdatehelper.environment_check())

    @patch.dict(os.environ, {
        "API_KEY": "test_api_key",
        "API_ENDPOINT": ""
    }, clear=True)
    def test_environment_check_missing_api_endpoint(self):
        self.assertFalse(azureupdatehelper.environment_check())


if __name__ == '__main__':
    unittest.main()
