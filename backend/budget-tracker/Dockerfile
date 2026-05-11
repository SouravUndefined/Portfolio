# Cloud-agnostic Docker image.
# Works on: AWS EC2, ECS/Fargate, GCP Cloud Run, Azure Container Apps, or any host with Docker.
FROM python:3.12-slim

WORKDIR /app

# System deps required by PyMuPDF for PDF rendering
RUN apt-get update && apt-get install -y --no-install-recommends \
    libgl1 \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies first (layer-cached unless requirements change)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY app.py spending_pipeline.py generate_report.py data_loader.py ./

# Temp directory for generated files (CSV + PDF reports)
ENV FILES_DIR=/tmp/spending-files

EXPOSE 8000

# uvicorn with 2 workers — swap to gunicorn for higher concurrency if needed
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "2"]
