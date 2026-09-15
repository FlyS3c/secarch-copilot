FROM python:3.12-slim@sha256:78387bc3881b8273120a12ebe6c1ab22b018ccc2c9adf565ae1ac9b536e184ea AS runtime

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

RUN groupadd --system secarch \
    && useradd --system --gid secarch --create-home secarch \
    && mkdir --parents /data \
    && chown secarch:secarch /data

WORKDIR /app

COPY requirements-linux.txt requirements.txt

RUN python -m pip install \
    --no-cache-dir \
    --require-hashes \
    --requirement requirements.txt

COPY --chown=secarch:secarch app ./app

USER secarch

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --start-period=15s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/health', timeout=3)"

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]