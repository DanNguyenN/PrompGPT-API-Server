FROM python:3.9-slim-buster
# Allow statements and log messages to immediately appear in the logs
ENV PYTHONUNBUFFERED True

COPY ./app /app

COPY ./very_important_key.json /app/very_important_key.json

ENV GOOGLE_APPLICATION_CREDENTIALS=/app/very_important_key.json

# 
COPY ./requirements.txt /app/requirements.txt

# 
RUN pip install --no-cache-dir --upgrade -r /app/requirements.txt

# 

# Set the number of Uvicorn workers to 1
ENV UVICORN_WORKERS=1

# Set the number of Gunicorn workers to 1
ENV WEB_CONCURRENCY=1

CMD ["python", "app/main.py"]