FROM python:3.12-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    libgl1 libglib2.0-0 && \
    rm -rf /var/lib/apt/lists/*

COPY pyproject.toml .
COPY lensforge/ lensforge/
COPY custom/ custom/
COPY tests/ tests/

RUN pip install --no-cache-dir ".[dev]"

# Ensure custom/ extensions are importable
ENV PYTHONPATH=/app

EXPOSE 8000

CMD ["uvicorn", "lensforge.app:create_app", "--factory", "--host", "0.0.0.0", "--port", "8000"]
