FROM python:3.13-alpine

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 

WORKDIR /app

COPY requirements.txt .
RUN apk update && apk upgrade --no-cache && \
    pip install --upgrade pip --no-cache-dir && \ 
    pip install --no-cache-dir -r requirements.txt

COPY . .

RUN adduser -D -u 1001 mrrobot
USER mrrobot

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
