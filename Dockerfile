# Dockerfile
FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

# Copy the add_meta_tags_and_header_banner.py script
COPY add_meta_tags_and_header_banner.py .

# Copy the create_static_files.py script
COPY create_static_files.py .

# Run the script to add meta tags and header banner
RUN python add_meta_tags_and_header_banner.py --path /usr/local/lib/python3.12/site-packages/streamlit/static/index.html

# Run the script to create static files (robots.txt and sitemap.xml)
RUN python create_static_files.py

COPY . .

CMD ["script/server"]
