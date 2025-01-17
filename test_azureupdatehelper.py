import unittest
from unittest.mock import patch, MagicMock
import azureupdatehelper
import os
from datetime import datetime
from unittest.mock import patch

class TestAzureUpdateHelper(unittest.TestCase):
  def test_placeholder(self):
    self.assertTrue(True)

  @patch('azureupdatehelper.client.chat.completions.create')
  @patch('azureupdatehelper.requests.get')
  def test_read_and_summary(self, mock_get, mock_openai):
    with patch.dict(os.environ, {'DEPLOYMENT_NAME': 'test-deployment-name'}):
      mock_response = MagicMock()
      mock_response.json.return_value = {
        'title': 'Test Title',
        'description': '<p>Test Description</p>',
        'created': '2023-01-01T00:00:00Z',
        'modified': '2023-01-02T00:00:00Z',
        'products': ['Product1', 'Product2']
      }
      mock_get.return_value = mock_response
      mock_openai.return_value = MagicMock(
        choices=[MagicMock(message=MagicMock(content='Summary of the update.'))]
      )

      url = 'http://example.com/?id=abc123'
      result = azureupdatehelper.read_and_summary(url)

      expected_url = "https://www.microsoft.com/releasecommunications/api/v2/azure/abc123"
      mock_get.assert_called_once_with(
        expected_url,
        headers={"User-Agent": "Safari/605.1.15"}
      )

    self.assertEqual(result['url'], url)
    self.assertEqual(result['apiUrl'], expected_url)
    self.assertEqual(result['docId'], 'abc123')
    self.assertEqual(result['title'], 'Test Title')
    self.assertEqual(result['description'], 'Test Description')
    self.assertEqual(result['products'], ['Product1', 'Product2'])
    self.assertEqual(result['publishedDate'], '2023-01-01T00:00:00Z')
    self.assertEqual(result['updatedDate'], '2023-01-02T00:00:00Z')
    self.assertEqual(result['summary'], 'Summary of the update.')

class TestEnvironmentCheck(unittest.TestCase):
  @patch.dict(os.environ, {
    "API_KEY": "test_api_key",
    "API_VERSION": "test_api_version",
    "API_ENDPOINT": "test_api_endpoint",
    "DEPLOYMENT_NAME": "test_deployment_name"
  }, clear=True)
  def test_environment_check_all_set(self):
    self.assertTrue(azureupdatehelper.environment_check())

  @patch.dict(os.environ, {
    "API_KEY": "",
    "API_VERSION": "test_api_version",
    "API_ENDPOINT": "test_api_endpoint",
    "DEPLOYMENT_NAME": "test_deployment_name"
  }, clear=True)
  def test_environment_check_missing_api_key(self):
    self.assertFalse(azureupdatehelper.environment_check())

  @patch.dict(os.environ, {
    "API_KEY": "test_api_key",
    "API_VERSION": "",
    "API_ENDPOINT": "test_api_endpoint",
    "DEPLOYMENT_NAME": "test_deployment_name"
  }, clear=True)
  def test_environment_check_missing_api_version(self):
    self.assertFalse(azureupdatehelper.environment_check())

  @patch.dict(os.environ, {
    "API_KEY": "test_api_key",
    "API_VERSION": "test_api_version",
    "API_ENDPOINT": "",
    "DEPLOYMENT_NAME": "test_deployment_name"
  }, clear=True)
  def test_environment_check_missing_api_endpoint(self):
    self.assertFalse(azureupdatehelper.environment_check())

  @patch.dict(os.environ, {
    "API_KEY": "test_api_key",
    "API_VERSION": "test_api_version",
    "API_ENDPOINT": "test_api_endpoint",
    "DEPLOYMENT_NAME": ""
  }, clear=True)
  def test_environment_check_missing_deployment_name(self):
    self.assertFalse(azureupdatehelper.environment_check())

if __name__ == '__main__':
  unittest.main()
