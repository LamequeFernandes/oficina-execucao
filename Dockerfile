FROM python:3.12-slim

# Instalar dependências SSL/TLS
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    ca-certificates \
    openssl \
    libssl-dev && \
    update-ca-certificates && \
    rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt && \
    pip install --no-cache-dir --upgrade certifi

COPY app /app

CMD ["ddtrace-run", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8002"]
