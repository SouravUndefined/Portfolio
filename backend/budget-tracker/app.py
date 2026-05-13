"""
Personal Spending Analyser — FastAPI backend for EC2.
Single synchronous endpoint, runs the spending pipeline + report generator,
returns download URLs for the CSV and PDF report.
"""

import os
import sys
import shutil
import time
import uuid
from pathlib import Path
from threading import Thread
from typing import List

sys.setrecursionlimit(5000)

from fastapi import FastAPI, File, HTTPException, Request, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from dotenv import load_dotenv

load_dotenv()

# ── config ────────────────────────────────────────────────────────────────────
FILES_DIR        = Path(os.environ.get("FILES_DIR", "/var/lib/spending-api/files"))
ALLOWED_ORIGINS  = [o.strip() for o in os.environ.get("ALLOWED_ORIGINS", "*").split(",")]
MAX_FILE_SIZE    = 15 * 1024 * 1024   # 15 MB
MAX_PDF_PAGES    = 50
FILE_TTL_SECONDS = 3600               # delete results after 1 hour

FILES_DIR.mkdir(parents=True, exist_ok=True)


# ── background cleanup thread ────────────────────────────────────────────────
def _cleanup_loop():
    while True:
        try:
            now = time.time()
            for job_dir in FILES_DIR.iterdir():
                if job_dir.is_dir() and (now - job_dir.stat().st_mtime) > FILE_TTL_SECONDS:
                    shutil.rmtree(job_dir, ignore_errors=True)
        except Exception:
            pass
        time.sleep(300)   # every 5 minutes


Thread(target=_cleanup_loop, daemon=True).start()


# ── FastAPI app ──────────────────────────────────────────────────────────────
app = FastAPI(title="Spending Analyser")

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_origin_regex=r"http://localhost:\d+",
    allow_credentials=False,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/analyse")
async def analyse(request: Request, files: List[UploadFile] = File(...)):
    """Process one or more bank/UPI/credit-card PDFs (+ optional spreadsheet) and return download URLs."""

    # 1. Consent guard — frontend must send this header after user explicitly agrees
    consent = request.headers.get("X-Consent-Given", "").strip().lower()
    if consent != "true":
        raise HTTPException(400, "Consent not provided. Please accept the data processing terms before uploading.")

    # 2. Must have at least one file
    if not files:
        raise HTTPException(400, "No files provided.")

    # 3. Set up workspace
    job_id  = str(uuid.uuid4())
    job_dir = FILES_DIR / job_id
    job_dir.mkdir()
    os.chmod(job_dir, 0o700)
    saved_sources = []

    try:
        # 3. Validate, read, and save each file
        for upload in files:
            fname = upload.filename or ""
            fname_lower = fname.lower()
            is_pdf   = fname_lower.endswith(".pdf")
            is_sheet = fname_lower.endswith((".xlsx", ".xls", ".csv"))

            if not is_pdf and not is_sheet:
                raise HTTPException(400, f"'{fname}': only PDF, Excel, or CSV files are accepted.")

            content = await upload.read()
            if len(content) > MAX_FILE_SIZE:
                raise HTTPException(413, f"'{fname}' is too large. Max {MAX_FILE_SIZE // (1024*1024)} MB.")
            if len(content) < 100:
                raise HTTPException(400, f"'{fname}' appears to be empty.")

            dest = job_dir / fname
            dest.write_bytes(content)
            saved_sources.append(dest)

        # 4. Page-count guard for every PDF (Groq API cost protection)
        import fitz
        for src in saved_sources:
            if src.suffix.lower() == ".pdf":
                doc = fitz.open(src)
                n_pages = len(doc)
                doc.close()
                if n_pages > MAX_PDF_PAGES:
                    raise HTTPException(400, f"'{src.name}' has {n_pages} pages — max {MAX_PDF_PAGES} allowed.")

        # 5. Run spending pipeline across all uploaded files
        import spending_pipeline as sp
        pdfs, offline = sp.detect_files(str(job_dir))
        all_txns = []
        for p in pdfs:
            all_txns.extend(sp.parse_pdf_vision(p))
        if offline:
            all_txns.extend(sp.parse_offline(offline))

        if not all_txns:
            raise HTTPException(400, "No transactions found in the uploaded files.")

        import pandas as pd
        df         = pd.DataFrame(all_txns)
        df         = sp.enrich_dataframe(df)
        dates      = pd.to_datetime(df["Date"])
        year_month = dates.dt.strftime("%Y%m").mode()[0]
        csv_name   = f"spending_{year_month}.csv"
        csv_path   = job_dir / csv_name
        df.to_csv(csv_path, index=False, encoding="utf-8-sig")
        os.chmod(csv_path, 0o600)

        # 6. Generate PDF report
        import generate_report as gr
        report_name = f"spending_report_{year_month}.pdf"
        report_path = job_dir / report_name
        gr.generate(str(csv_path), str(report_path))
        os.chmod(report_path, 0o600)

        # 7. Delete all uploaded source files (keep only CSV + report)
        for src in saved_sources:
            src.unlink(missing_ok=True)

        # 8. Return download URLs
        return {
            "csv_url":    f"/files/{job_id}/{csv_name}",
            "report_url": f"/files/{job_id}/{report_name}",
            "row_count":  len(df),
            "file_count": len(saved_sources),
        }

    except HTTPException:
        shutil.rmtree(job_dir, ignore_errors=True)
        raise
    except Exception as e:
        shutil.rmtree(job_dir, ignore_errors=True)
        raise HTTPException(500, f"Processing failed: {e}")


@app.get("/files/{job_id}/{filename}")
def download(job_id: str, filename: str):
    """Stream a generated CSV or report PDF back to the browser."""
    if len(job_id) != 36:
        raise HTTPException(400, "Invalid job_id.")
    if "/" in filename or ".." in filename or "\\" in filename:
        raise HTTPException(400, "Invalid filename.")

    path = FILES_DIR / job_id / filename
    if not path.exists():
        raise HTTPException(404, "File not found or expired.")

    media = "text/csv" if filename.endswith(".csv") else "application/pdf"
    return FileResponse(path, filename=filename, media_type=media)
