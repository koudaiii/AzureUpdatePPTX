#!/usr/bin/env python3
"""
Script to create static files (robots.txt and sitemap.xml) in Streamlit app root directory.
This script should be run during Docker build process.
"""

import os
import logging
import sys
import datetime
from os import getenv

# Logging configuration
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Configuration
BASE_URL = getenv('BASE_URL', 'https://azure.koudaiii.com')
current_date = datetime.date.today().isoformat()


def get_robots_txt_content():
    """Return robots.txt content"""
    return f"""User-agent: *
Allow: /

# This is a web application for generating Azure Updates summaries
# All content is dynamically generated and safe for crawling
Sitemap: {BASE_URL}/sitemap.xml
"""


def get_sitemap_xml_content():
    """Return sitemap.xml content"""
    # Supported languages with their priorities
    languages = [
        ('', 1.0),  # Main page (no lang parameter)
        ('ja', 0.9),  # Japanese (default)
        ('en', 0.9),  # English
        ('ko', 0.8),  # Korean
        ('zh-cn', 0.8),  # Chinese Simplified
        ('zh-tw', 0.8),  # Chinese Traditional
        ('th', 0.7),  # Thai
        ('vi', 0.7),  # Vietnamese
        ('id', 0.7),  # Indonesian
        ('hi', 0.7),  # Hindi
    ]

    sitemap_content = """<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">"""

    for lang, priority in languages:
        if lang:
            url = f"{BASE_URL}/?lang={lang}"
        else:
            url = f"{BASE_URL}/"

        sitemap_content += f"""
  <url>
    <loc>{url}</loc>
    <lastmod>{current_date}</lastmod>
    <changefreq>weekly</changefreq>
    <priority>{priority}</priority>
  </url>"""

    sitemap_content += """
</urlset>
"""
    return sitemap_content


def find_streamlit_static_root():
    """Find Streamlit's static directory using package introspection"""
    # More robust path detection using streamlit package
    try:
        import streamlit
        streamlit_path = os.path.dirname(streamlit.__file__)
        static_path = os.path.join(streamlit_path, 'static')
        if os.path.exists(static_path):
            logging.info(f"Found Streamlit static directory via package introspection: {static_path}")
            return static_path
        else:
            logging.warning(f"Streamlit static directory not found at expected location: {static_path}")
    except ImportError:
        logging.error("Streamlit package not found - cannot determine static directory")
        return None

    # Fallback to hardcoded paths (for edge cases)
    possible_static_paths = [
        "/app/streamlit/frontend/build/static",
        "/usr/local/lib/python3.9/site-packages/streamlit/static",
        "/usr/local/lib/python3.8/dist-packages/streamlit/static",
        "/usr/local/lib/python3.12/site-packages/streamlit/static"
    ]

    logging.info("Falling back to hardcoded path search...")
    for static_path in possible_static_paths:
        if os.path.exists(static_path):
            logging.info(f"Found Streamlit static directory via fallback: {static_path}")
            return static_path

    logging.error("Streamlit static directory not found")
    return None


def create_static_files(target_dir=None):
    """Create robots.txt and sitemap.xml files in the specified directory

    Args:
        target_dir: Target directory to create files in. If None, will try to find Streamlit static dir.
    """
    if target_dir is None:
        target_dir = find_streamlit_static_root()
        if target_dir is None:
            logging.error("Could not find target directory for static files")
            return False

    if not os.path.exists(target_dir):
        logging.error(f"Target directory does not exist: {target_dir}")
        return False

    success = True

    # Create robots.txt
    robots_path = os.path.join(target_dir, "robots.txt")
    try:
        with open(robots_path, 'w', encoding='utf-8') as f:
            f.write(get_robots_txt_content())
        logging.info(f"Created robots.txt at {robots_path}")
    except Exception as e:
        logging.error(f"Failed to create robots.txt: {e}")
        success = False

    # Create sitemap.xml
    sitemap_path = os.path.join(target_dir, "sitemap.xml")
    try:
        with open(sitemap_path, 'w', encoding='utf-8') as f:
            f.write(get_sitemap_xml_content())
        logging.info(f"Created sitemap.xml at {sitemap_path}")
    except Exception as e:
        logging.error(f"Failed to create sitemap.xml: {e}")
        success = False

    return success


def main():
    """Main function"""
    import argparse
    parser = argparse.ArgumentParser(description='Create static files for Streamlit')
    parser.add_argument('--target-dir', help='Target directory to create files in (optional)')
    args = parser.parse_args()

    success = create_static_files(args.target_dir)

    if success:
        print("Static files (robots.txt and sitemap.xml) created successfully")
        sys.exit(0)
    else:
        print("Failed to create static files")
        sys.exit(1)


if __name__ == "__main__":
    main()
