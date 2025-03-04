# Dockerfile
FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

# Copy the add_meta_tags_and_header-banner.py script
COPY add_meta_tags_and_header-banner.py .

# Run the script to add meta tags and header banner
RUN python add_meta_tags_and_header-banner.py

COPY . .

CMD ["script/server"]
