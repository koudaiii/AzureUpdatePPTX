#!/usr/bin/env python3
"""
Script to create static files (robots.txt and sitemap.xml) in Streamlit app root directory.
This script should be run during Docker build process.
"""

import os
import logging
import sys

# Logging configuration
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


def get_robots_txt_content():
    """Return robots.txt content"""
    return """User-agent: *
Allow: /

# This is a web application for generating Azure Updates summaries
# All content is dynamically generated and safe for crawling
Sitemap: https://azure.koudaiii.com/sitemap.xml
"""


def get_sitemap_xml_content():
    """Return sitemap.xml content"""
    return """<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
  <url>
    <loc>https://azure.koudaiii.com/</loc>
    <lastmod>2025-01-28</lastmod>
    <changefreq>weekly</changefreq>
    <priority>1.0</priority>
  </url>
  <url>
    <loc>https://azure.koudaiii.com/?lang=ja</loc>
    <lastmod>2025-01-28</lastmod>
    <changefreq>weekly</changefreq>
    <priority>0.9</priority>
  </url>
  <url>
    <loc>https://azure.koudaiii.com/?lang=en</loc>
    <lastmod>2025-01-28</lastmod>
    <changefreq>weekly</changefreq>
    <priority>0.9</priority>
  </url>
  <url>
    <loc>https://azure.koudaiii.com/?lang=ko</loc>
    <lastmod>2025-01-28</lastmod>
    <changefreq>weekly</changefreq>
    <priority>0.8</priority>
  </url>
  <url>
    <loc>https://azure.koudaiii.com/?lang=zh-cn</loc>
    <lastmod>2025-01-28</lastmod>
    <changefreq>weekly</changefreq>
    <priority>0.8</priority>
  </url>
  <url>
    <loc>https://azure.koudaiii.com/?lang=zh-tw</loc>
    <lastmod>2025-01-28</lastmod>
    <changefreq>weekly</changefreq>
    <priority>0.8</priority>
  </url>
  <url>
    <loc>https://azure.koudaiii.com/?lang=th</loc>
    <lastmod>2025-01-28</lastmod>
    <changefreq>weekly</changefreq>
    <priority>0.7</priority>
  </url>
  <url>
    <loc>https://azure.koudaiii.com/?lang=vi</loc>
    <lastmod>2025-01-28</lastmod>
    <changefreq>weekly</changefreq>
    <priority>0.7</priority>
  </url>
  <url>
    <loc>https://azure.koudaiii.com/?lang=id</loc>
    <lastmod>2025-01-28</lastmod>
    <changefreq>weekly</changefreq>
    <priority>0.7</priority>
  </url>
  <url>
    <loc>https://azure.koudaiii.com/?lang=hi</loc>
    <lastmod>2025-01-28</lastmod>
    <changefreq>weekly</changefreq>
    <priority>0.7</priority>
  </url>
</urlset>
"""


def find_streamlit_static_root():
    """Find Streamlit's static file root directory"""
    # First, try to find index.html and get its directory
    possible_index_paths = [
        "/app/streamlit/frontend/build/index.html",
        "/usr/local/lib/python3.9/site-packages/streamlit/static/index.html",
        "/usr/local/lib/python3.8/dist-packages/streamlit/static/index.html",
        "/usr/local/lib/python3.12/site-packages/streamlit/static/index.html"
    ]
    
    for index_path in possible_index_paths:
        if os.path.exists(index_path):
            static_dir = os.path.dirname(index_path)
            logging.info(f"Found Streamlit static directory via index.html: {static_dir}")
            return static_dir
    
    # Fallback to direct static directory search
    possible_static_paths = [
        "/app/streamlit/frontend/build/static",
        "/usr/local/lib/python3.9/site-packages/streamlit/static",
        "/usr/local/lib/python3.8/dist-packages/streamlit/static",
        "/usr/local/lib/python3.12/site-packages/streamlit/static"
    ]
    
    for static_path in possible_static_paths:
        if os.path.exists(static_path):
            logging.info(f"Found Streamlit static directory: {static_path}")
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
    parser = argparse.ArgumentParser(description='Create static files for Streamlit app')
    parser.add_argument('--target-dir', help='Target directory to create files in (optional, will auto-detect if not specified)')
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
