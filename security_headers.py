"""
Security headers module for AzureUpdatePPTX Streamlit application.

This module provides functionality to add security headers via HTTP response
modification rather than meta tags for better security compliance.
"""

import streamlit as st
import logging


def add_security_headers():
    """
    Add security headers to Streamlit responses.

    This function sets the necessary security headers including:
    - X-Content-Type-Options: nosniff
    - X-Frame-Options: DENY (for frame protection)
    """
    try:
        # Get the current session context
        ctx = st.runtime.get_instance()._session_mgr.get_session_info(
            st.runtime.get_instance()._session_mgr.active_session_id
        )

        # Add headers to the response
        if hasattr(ctx, '_response'):
            ctx._response.headers['X-Content-Type-Options'] = 'nosniff'
            ctx._response.headers['X-Frame-Options'] = 'DENY'
            logging.info("Security headers added successfully")
        else:
            logging.warning("Unable to access response object for header modification")

    except Exception as e:
        logging.error(f"Failed to add security headers: {e}")


def setup_security_headers_middleware():
    """
    Set up middleware to automatically add security headers to all responses.
    """
    # This is a placeholder for future implementation
    # Streamlit doesn't have built-in middleware support, so we'll use
    # HTML injection for now
    pass


def inject_security_headers_html():
    """
    Inject frame-busting protection via JavaScript.

    Note: Security headers like X-Frame-Options and CSP frame-ancestors
    should be set via HTTP headers, not meta tags for proper enforcement.

    Returns:
        str: HTML string with frame-busting protection
    """
    return """
    <script>
        // Frame-busting protection
        if (window.top !== window.self) {
            // If the page is in an iframe, break out of it
            try {
                window.top.location = window.self.location;
            } catch (e) {
                // If cross-origin error, at least hide the content
                document.body.style.display = 'none';
            }
        }
    </script>
    """


def init_security_headers():
    """
    Initialize security headers for the Streamlit application.

    This function should be called early in the main.py file.
    """
    try:
        # Inject security headers HTML via markdown with unsafe_allow_html
        # This is safer and more reliable than components approach
        st.markdown(inject_security_headers_html(), unsafe_allow_html=True)

        # Log initialization
        logging.info("Security headers initialized")

    except Exception as e:
        logging.error(f"Failed to initialize security headers: {e}")
        # Don't re-raise the exception to avoid breaking the app startup
