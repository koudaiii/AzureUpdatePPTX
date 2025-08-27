import unittest
from unittest.mock import patch, MagicMock
import logging
from io import StringIO
import security_headers


class TestSecurityHeaders(unittest.TestCase):

    def setUp(self):
        """Setup before tests"""
        # Create string buffer to capture log messages
        self.log_stream = StringIO()
        self.log_handler = logging.StreamHandler(self.log_stream)

        # Setup logger
        self.logger = logging.getLogger()
        self.logger.addHandler(self.log_handler)
        self.logger.setLevel(logging.DEBUG)

    def tearDown(self):
        """Cleanup after tests"""
        # Remove handler to prevent interference between tests
        self.logger.removeHandler(self.log_handler)

    @patch('streamlit.runtime.get_instance')
    def test_add_security_headers_success(self, mock_get_instance):
        """Test successful addition of security headers"""
        # Mock the response object
        mock_response = MagicMock()
        mock_response.headers = {}

        # Mock the session info
        mock_session_info = MagicMock()
        mock_session_info._response = mock_response

        # Mock the session manager
        mock_session_mgr = MagicMock()
        mock_session_mgr.active_session_id = 'test_session_id'
        mock_session_mgr.get_session_info.return_value = mock_session_info

        # Mock the runtime instance
        mock_instance = MagicMock()
        mock_instance._session_mgr = mock_session_mgr
        mock_get_instance.return_value = mock_instance

        # Call the function
        security_headers.add_security_headers()

        # Verify headers were added
        self.assertEqual(mock_response.headers['X-Content-Type-Options'], 'nosniff')
        self.assertEqual(mock_response.headers['X-Frame-Options'], 'DENY')

        # Verify logging
        log_contents = self.log_stream.getvalue()
        self.assertIn('Security headers added successfully', log_contents)

    @patch('streamlit.runtime.get_instance')
    def test_add_security_headers_no_response_object(self, mock_get_instance):
        """Test when response object is not accessible"""
        # Mock session info without _response attribute
        mock_session_info = MagicMock()
        del mock_session_info._response

        # Mock the session manager
        mock_session_mgr = MagicMock()
        mock_session_mgr.active_session_id = 'test_session_id'
        mock_session_mgr.get_session_info.return_value = mock_session_info

        # Mock the runtime instance
        mock_instance = MagicMock()
        mock_instance._session_mgr = mock_session_mgr
        mock_get_instance.return_value = mock_instance

        # Call the function
        security_headers.add_security_headers()

        # Verify warning was logged
        log_contents = self.log_stream.getvalue()
        self.assertIn('Unable to access response object for header modification', log_contents)

    @patch('streamlit.runtime.get_instance')
    def test_add_security_headers_exception(self, mock_get_instance):
        """Test exception handling in add_security_headers"""
        # Make get_instance raise an exception
        mock_get_instance.side_effect = Exception("Test exception")

        # Call the function
        security_headers.add_security_headers()

        # Verify error was logged
        log_contents = self.log_stream.getvalue()
        self.assertIn('Failed to add security headers: Test exception', log_contents)


class TestSecurityHeadersMiddleware(unittest.TestCase):

    def test_setup_security_headers_middleware(self):
        """Test middleware setup placeholder"""
        # This function is currently a placeholder, so we just verify it doesn't raise exceptions
        try:
            security_headers.setup_security_headers_middleware()
        except Exception as e:
            self.fail(f"setup_security_headers_middleware raised an exception: {e}")


class TestInjectSecurityHeadersHTML(unittest.TestCase):

    def test_inject_security_headers_html_content(self):
        """Test HTML injection content"""
        html_content = security_headers.inject_security_headers_html()

        # Verify it returns a string
        self.assertIsInstance(html_content, str)

        # Verify it contains expected elements
        self.assertIn('<script>', html_content)
        self.assertIn('window.top !== window.self', html_content)
        self.assertIn('Frame-busting protection', html_content)
        self.assertIn('</script>', html_content)

    def test_inject_security_headers_html_structure(self):
        """Test HTML injection structure and security measures"""
        html_content = security_headers.inject_security_headers_html()

        # Verify frame-busting protection is included
        self.assertIn('window.top.location = window.self.location', html_content)

        # Verify frame-busting fallback
        self.assertIn('document.body.style.display', html_content)

        # Verify error handling
        self.assertIn('try {', html_content)
        self.assertIn('} catch (e) {', html_content)


class TestInitSecurityHeaders(unittest.TestCase):

    def setUp(self):
        """Setup before tests"""
        # Create string buffer to capture log messages
        self.log_stream = StringIO()
        self.log_handler = logging.StreamHandler(self.log_stream)

        # Setup logger
        self.logger = logging.getLogger()
        self.logger.addHandler(self.log_handler)
        self.logger.setLevel(logging.DEBUG)

    def tearDown(self):
        """Cleanup after tests"""
        # Remove handler to prevent interference between tests
        self.logger.removeHandler(self.log_handler)

    @patch('streamlit.markdown')
    def test_init_security_headers_success(self, mock_markdown):
        """Test successful initialization of security headers"""
        # Call the function
        security_headers.init_security_headers()

        # Verify st.markdown was called
        mock_markdown.assert_called_once()

        # Verify the HTML content was passed
        call_args = mock_markdown.call_args
        html_content = call_args[0][0]
        self.assertIn('<script>', html_content)
        self.assertIn('Frame-busting protection', html_content)

        # Verify unsafe_allow_html=True was passed
        self.assertTrue(call_args[1]['unsafe_allow_html'])

        # Verify logging
        log_contents = self.log_stream.getvalue()
        self.assertIn('Security headers initialized', log_contents)

    @patch('streamlit.markdown')
    def test_init_security_headers_exception(self, mock_markdown):
        """Test exception handling in init_security_headers"""
        # Make st.markdown raise an exception
        mock_markdown.side_effect = Exception("Streamlit error")

        # Call the function
        security_headers.init_security_headers()

        # Verify error was logged
        log_contents = self.log_stream.getvalue()
        self.assertIn('Failed to initialize security headers: Streamlit error', log_contents)


class TestSecurityHeadersIntegration(unittest.TestCase):

    def test_html_injection_contains_all_security_measures(self):
        """Test that HTML injection contains all necessary security measures"""
        html_content = security_headers.inject_security_headers_html()

        # List of expected security features (updated for simplified frame-busting)
        security_features = [
            'window.top !== window.self',  # Frame busting condition
            'window.top.location = window.self.location',  # Frame busting action
            'document.body.style.display = \'none\'',  # Content hiding fallback
        ]

        for feature in security_features:
            with self.subTest(feature=feature):
                self.assertIn(feature, html_content)

    @patch('streamlit.markdown')
    @patch('streamlit.runtime.get_instance')
    def test_full_security_headers_workflow(self, mock_get_instance, mock_markdown):
        """Test the complete workflow of security headers implementation"""
        # Setup mocks for add_security_headers
        mock_response = MagicMock()
        mock_response.headers = {}
        mock_session_info = MagicMock()
        mock_session_info._response = mock_response
        mock_session_mgr = MagicMock()
        mock_session_mgr.active_session_id = 'test_session_id'
        mock_session_mgr.get_session_info.return_value = mock_session_info
        mock_instance = MagicMock()
        mock_instance._session_mgr = mock_session_mgr
        mock_get_instance.return_value = mock_instance

        # Test both functions work together
        security_headers.init_security_headers()
        security_headers.add_security_headers()

        # Verify HTML injection was called
        mock_markdown.assert_called_once()

        # Verify headers were set
        self.assertEqual(mock_response.headers['X-Content-Type-Options'], 'nosniff')
        self.assertEqual(mock_response.headers['X-Frame-Options'], 'DENY')


if __name__ == '__main__':
    unittest.main()
