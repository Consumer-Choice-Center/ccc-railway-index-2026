# syntax=docker/dockerfile:1
FROM python:3.12-slim@sha256:2fe5997d249a808b8eeea52c58a1dbffbba28754dc11699ef5c029f2d818ce79 AS builder

WORKDIR /install
COPY requirements.txt .
RUN python -m pip install --no-cache-dir --prefix=/install -r requirements.txt

FROM python:3.12-slim@sha256:2fe5997d249a808b8eeea52c58a1dbffbba28754dc11699ef5c029f2d818ce79

RUN groupadd --system --gid 10001 app \
    && useradd --system --uid 10001 --gid app --home-dir /home/app --create-home app

COPY --from=builder /install /usr/local

WORKDIR /app
COPY --chown=app:app . .

USER app

ENV HOME=/home/app \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    STREAMLIT_BROWSER_GATHER_USAGE_STATS=false \
    STREAMLIT_SERVER_ADDRESS=0.0.0.0 \
    STREAMLIT_SERVER_HEADLESS=true \
    STREAMLIT_SERVER_PORT=8501

EXPOSE 8501

HEALTHCHECK --interval=30s --timeout=5s --retries=3 --start-period=15s \
    CMD ["python", "-c", "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8501/_stcore/health', timeout=3)"]

ENTRYPOINT ["streamlit", "run", "app.py"]
