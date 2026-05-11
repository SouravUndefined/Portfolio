FROM python:3.12-slim

# Copy uv binary from the official image
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

WORKDIR /app

# System libs needed by PyMuPDF and matplotlib
RUN apt-get update && apt-get install -y --no-install-recommends \
    libgl1 \
    libglib2.0-0 \
    fontconfig \
    && rm -rf /var/lib/apt/lists/*

# Install Python deps first (Docker layer cache — only reruns if lock file changes)
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev

# Copy application code
COPY app.py spending_pipeline.py generate_report.py data_loader.py ./

ENV FILES_DIR=/tmp/spending-files

EXPOSE 8000

CMD ["/app/.venv/bin/gunicorn", "app:app", \
     "-w", "2", \
     "-k", "uvicorn.workers.UvicornWorker", \
     "--bind", "0.0.0.0:8000", \
     "--timeout", "1200"]
