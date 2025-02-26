# Dockerfile
FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

# Copy the add_meta_tags.py script
COPY add_meta_tags.py .

# Run the script to add meta tags
RUN python add_meta_tags.py

COPY . .

CMD ["script/server"]
