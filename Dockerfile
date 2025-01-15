# Dockerfile
FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

COPY . .

CMD ["streamlit", "run", "main.py", "--server.port=80", "--server.enableCORS=false"]