FROM python:3.11-slim

WORKDIR /app

ENV PYTHONUNBUFFERED=1

# Install minimal runtime deps
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

COPY services/ingest_service /app

RUN pip install --no-cache-dir flask prometheus-client

EXPOSE 8080

CMD ["python", "app.py"]
