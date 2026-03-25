FROM python:3.13-alpine@sha256:bb1f2fdb1065c85468775c9d680dcd344f6442a2d1181ef7916b60a623f11d40

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 

WORKDIR /app

COPY requirements.txt .
RUN apk update && apk upgrade --no-cache && \
    pip install --no-cache-dir --upgrade pip==25.0.1 && \ 
    pip install --no-cache-dir -r requirements.txt

COPY . .

RUN adduser -D -u 1001 mrrobot
USER mrrobot

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
