# Dockerfile
FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

# Copy the add_meta_tags_and_header_banner.py script
COPY add_meta_tags_and_header_banner.py .

# Run the script to add meta tags and header banner
RUN python add_meta_tags_and_header_banner.py --path /usr/local/lib/python3.12/site-packages/streamlit/static/index.html

COPY . .

CMD ["script/server"]
