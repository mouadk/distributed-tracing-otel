FROM python:3.11-slim@sha256:80bcf8d243a0d763a7759d6b99e5bf89af1869135546698be4bf7ff6c3f98a59 as builder

ENV PIP_DEFAULT_TIMEOUT=100 \
    PYTHONUNBUFFERED=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /builder

COPY pyproject.toml /builder/

RUN pip install --no-cache-dir poetry

RUN poetry config virtualenvs.create false && poetry install

FROM python:3.11-slim@sha256:80bcf8d243a0d763a7759d6b99e5bf89af1869135546698be4bf7ff6c3f98a59

COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin/uvicorn /usr/local/bin/uvicorn
COPY --from=builder /usr/local/bin/poetry /usr/local/bin/poetry

WORKDIR /workspace

COPY main.py /workspace/main.py
COPY docker-entry-point.sh /workspace/docker-entry-point.sh

RUN chmod +x /workspace/docker-entry-point.sh

ENTRYPOINT ["./docker-entry-point.sh"]
