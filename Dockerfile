FROM tiangolo/uvicorn-gunicorn-fastapi:python3.9-slim
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



#CMD ["uvicorn", "app.main:app", "--proxy-headers", "--host", "0.0.0.0", "--port", $PORT]