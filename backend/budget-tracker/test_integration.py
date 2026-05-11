"""
Integration tests — Spending Metrics Backend
=============================================
Uses real PDFs from local-database/budget-tracker/monthly-data/ and the real Groq vision API.
All pipeline tests share one session-level fixture so the Groq API
is called ONCE per PDF, not once per test.

Run all tests:
    uv run pytest test_integration.py -v

Run only fast API tests (no Groq call):
    uv run pytest test_integration.py::TestAPI -v

Run only slow pipeline tests:
    uv run pytest test_integration.py::TestPipeline -v

Run with visible print output:
    uv run pytest test_integration.py -v -s

Requirements:
    - backend/.env must have a valid API_KEY
    - local-database/budget-tracker/monthly-data/ must contain at least one PDF
"""

import os
import tempfile
from pathlib import Path

import pandas as pd
import pytest
from dotenv import load_dotenv

# Load .env before importing anything that reads env vars
load_dotenv(Path(__file__).parent / ".env")

MONTHLY_DATA = Path(__file__).parent.parent.parent / "local-database" / "budget-tracker" / "monthly-data"
EXPECTED_COLUMNS = [
    "Date", "Time", "Description", "Amount", "Type",
    "Category", "Subcategory", "Source", "Account", "Payment_Mode", "Bank",
    "Day", "Day_Name", "Day_of_Week", "Week_Number", "Week_Label",
    "Month", "Month_Name", "Year", "Quarter", "Year_Month",
    "Is_Weekend", "Time_Bucket", "Amount_Bucket",
    "Is_Recurring", "Spend_Type",
    "Is_Debit", "Is_Credit", "Is_Transfer", "Cumulative_Spend",
]


# ── helpers ───────────────────────────────────────────────────────────────────

def _get_pdfs() -> list[Path]:
    if not MONTHLY_DATA.exists():
        return []
    return sorted(MONTHLY_DATA.glob("*.pdf"))


def _has_api_key() -> bool:
    return bool(os.environ.get("API_KEY", "").strip())


# ── session fixtures ──────────────────────────────────────────────────────────

@pytest.fixture(scope="session")
def all_pdfs() -> list[Path]:
    pdfs = _get_pdfs()
    if not pdfs:
        pytest.skip("No PDF files found in local-database/budget-tracker/monthly-data/")
    return pdfs


@pytest.fixture(scope="session")
def pipeline_output(all_pdfs):
    """
    Run the full pipeline once for the entire test session.
    Returns a dict with raw transactions, enriched DataFrame,
    CSV path, and report PDF path — all in a temp directory.

    This fixture is slow (calls Groq API). All TestPipeline tests
    share this one result instead of re-running the pipeline.
    """
    if not _has_api_key():
        pytest.skip("API_KEY not set in backend/.env")

    import spending_pipeline as sp
    import generate_report as gr

    # 1. Parse all PDFs
    all_txns = []
    for pdf in all_pdfs:
        print(f"\n  [fixture] Parsing {pdf.name} ...")
        txns = sp.parse_pdf_vision(str(pdf))
        print(f"           → {len(txns)} transactions")
        all_txns.extend(txns)

    assert all_txns, "Pipeline returned zero transactions from all PDFs combined"

    # 2. Enrich
    df = pd.DataFrame(all_txns)
    df = sp.enrich_dataframe(df)

    # 3. Write CSV
    tmp = Path(tempfile.mkdtemp())
    dates = pd.to_datetime(df["Date"])
    year_month = dates.dt.strftime("%Y%m").mode()[0]

    csv_path = tmp / f"spending_{year_month}.csv"
    df.to_csv(csv_path, index=False, encoding="utf-8-sig")

    # 4. Generate PDF report
    report_path = tmp / f"spending_report_{year_month}.pdf"
    gr.generate(str(csv_path), str(report_path))

    return {
        "transactions": all_txns,
        "df":           df,
        "csv_path":     csv_path,
        "report_path":  report_path,
        "year_month":   year_month,
    }


@pytest.fixture(scope="session")
def api_client():
    """FastAPI TestClient — connects directly to the app (no Nginx)."""
    from fastapi.testclient import TestClient
    import app as spending_app
    return TestClient(spending_app.app)


# ══════════════════════════════════════════════════════════════════════════════
#  TestPipeline — verifies core extraction and enrichment logic
#  (slow: calls real Groq API once via session fixture)
# ══════════════════════════════════════════════════════════════════════════════

class TestPipeline:

    # ── source detection ─────────────────────────────────────────────────────

    def test_pdfs_found_in_local_database(self, all_pdfs):
        """local-database/budget-tracker/monthly-data/ contains at least one readable PDF."""
        assert len(all_pdfs) >= 1
        for p in all_pdfs:
            assert p.exists()
            assert p.stat().st_size > 1024, f"{p.name} is too small to be a real PDF"

    def test_detect_files_returns_pdfs(self, all_pdfs):
        """detect_files() picks up the same PDFs from the folder."""
        import spending_pipeline as sp
        detected_pdfs, _ = sp.detect_files(str(MONTHLY_DATA))
        assert len(detected_pdfs) == len(all_pdfs)

    def test_pdf_source_detection(self, all_pdfs):
        """Every PDF gets a non-empty source and a recognised payment mode."""
        import spending_pipeline as sp
        valid_modes = {"Credit Card", "Debit Card", "UPI", "Unknown"}
        for pdf in all_pdfs:
            source, mode = sp.detect_pdf_source(str(pdf))
            assert source, f"{pdf.name}: source is empty"
            assert mode in valid_modes, f"{pdf.name}: unexpected mode '{mode}'"

    # ── transaction extraction ────────────────────────────────────────────────

    def test_transactions_extracted(self, pipeline_output):
        """Pipeline extracts at least one transaction in total."""
        assert len(pipeline_output["transactions"]) > 0

    def test_each_pdf_yields_transactions(self, all_pdfs):
        """Each individual PDF produces at least one transaction."""
        if not _has_api_key():
            pytest.skip("API_KEY not set")
        import spending_pipeline as sp
        for pdf in all_pdfs:
            txns = sp.parse_pdf_vision(str(pdf))
            assert len(txns) > 0, f"No transactions from {pdf.name}"

    def test_transaction_required_fields(self, pipeline_output):
        """Every transaction dict has the required keys."""
        required = {"Date", "Description", "Amount", "Type",
                    "Source", "Category", "Subcategory", "Payment_Mode"}
        for i, txn in enumerate(pipeline_output["transactions"]):
            missing = required - txn.keys()
            assert not missing, f"Transaction #{i} missing keys: {missing}"

    def test_amounts_are_positive(self, pipeline_output):
        """No transaction has a zero or negative amount."""
        for txn in pipeline_output["transactions"]:
            assert txn["Amount"] > 0, (
                f"Non-positive amount {txn['Amount']} in '{txn['Description']}'"
            )

    def test_types_are_valid(self, pipeline_output):
        """Every transaction type is Debit, Credit, or Transfer."""
        valid = {"Debit", "Credit", "Transfer"}
        for txn in pipeline_output["transactions"]:
            assert txn["Type"] in valid, (
                f"Invalid type '{txn['Type']}' for '{txn['Description']}'"
            )

    def test_dates_are_recent(self, pipeline_output):
        """All dates are within the last 10 years (catches year-parsing bugs)."""
        from datetime import datetime
        cutoff = datetime(datetime.now().year - 10, 1, 1)
        for txn in pipeline_output["transactions"]:
            assert txn["Date"] >= cutoff, (
                f"Suspicious date {txn['Date']} for '{txn['Description']}'"
            )

    def test_no_duplicates(self, pipeline_output):
        """Deduplication removed repeated transactions (same date+desc+amount)."""
        txns = pipeline_output["transactions"]
        keys = [
            (
                t["Date"].strftime("%Y-%m-%d"),
                t["Description"][:40].upper(),
                round(t["Amount"], 2),
            )
            for t in txns
        ]
        assert len(keys) == len(set(keys)), "Duplicate transactions found after dedup"

    # ── enrichment ───────────────────────────────────────────────────────────

    def test_all_31_columns_present(self, pipeline_output):
        """Enriched DataFrame contains all 31 expected analytical columns."""
        df = pipeline_output["df"]
        for col in EXPECTED_COLUMNS:
            assert col in df.columns, f"Column '{col}' missing from enriched DataFrame"

    def test_is_debit_is_credit_flags(self, pipeline_output):
        """Is_Debit and Is_Credit flags are mutually exclusive."""
        df = pipeline_output["df"]
        both = df[(df["Is_Debit"] == 1) & (df["Is_Credit"] == 1)]
        assert len(both) == 0, "Some rows are flagged as both Debit and Credit"

    def test_amount_bucket_coverage(self, pipeline_output):
        """Every row has a non-empty Amount_Bucket."""
        df = pipeline_output["df"]
        assert df["Amount_Bucket"].notna().all()
        assert (df["Amount_Bucket"] != "").all()

    def test_spend_type_values(self, pipeline_output):
        """Spend_Type is either Essential or Discretionary."""
        df = pipeline_output["df"]
        debits = df[df["Type"] == "Debit"]
        assert debits["Spend_Type"].isin(["Essential", "Discretionary"]).all()

    def test_cumulative_spend_monotonic(self, pipeline_output):
        """Cumulative_Spend only ever increases or stays flat."""
        df = pipeline_output["df"]
        cum = df["Cumulative_Spend"].values
        assert all(cum[i] <= cum[i + 1] for i in range(len(cum) - 1)), (
            "Cumulative_Spend decreased — sort or calculation bug"
        )

    def test_categorisation_rate(self, pipeline_output):
        """Less than 30% of debit transactions should be Uncategorized."""
        df = pipeline_output["df"]
        debits = df[df["Type"] == "Debit"]
        if len(debits) == 0:
            pytest.skip("No debit transactions to check")
        uncat_pct = (debits["Category"] == "Uncategorized").mean() * 100
        assert uncat_pct < 30, (
            f"{uncat_pct:.1f}% of debits are Uncategorized — "
            "add missing keywords to CATEGORY_RULES"
        )

    # ── output files ─────────────────────────────────────────────────────────

    def test_csv_created(self, pipeline_output):
        """CSV output file exists and is non-empty."""
        csv_path = pipeline_output["csv_path"]
        assert csv_path.exists(), "CSV file was not created"
        assert csv_path.stat().st_size > 100

    def test_csv_reloadable(self, pipeline_output):
        """CSV can be read back and row count matches the enriched DataFrame."""
        csv_path = pipeline_output["csv_path"]
        reloaded = pd.read_csv(csv_path)
        assert len(reloaded) == len(pipeline_output["df"])
        for col in EXPECTED_COLUMNS:
            assert col in reloaded.columns, f"Column '{col}' missing from saved CSV"

    def test_report_pdf_created(self, pipeline_output):
        """PDF report file exists and is at least 50 KB."""
        report_path = pipeline_output["report_path"]
        assert report_path.exists(), "PDF report was not created"
        size_kb = report_path.stat().st_size / 1024
        assert size_kb > 50, f"Report PDF is only {size_kb:.1f} KB — looks empty"

    def test_report_starts_with_pdf_header(self, pipeline_output):
        """PDF report starts with the %PDF magic bytes."""
        report_path = pipeline_output["report_path"]
        with open(report_path, "rb") as f:
            header = f.read(4)
        assert header == b"%PDF", "Report file is not a valid PDF"


# ══════════════════════════════════════════════════════════════════════════════
#  TestAPI — verifies the FastAPI endpoints
#  (mostly fast; one slow test uploads a real PDF end-to-end)
# ══════════════════════════════════════════════════════════════════════════════

class TestAPI:

    # ── fast tests (no Groq API) ─────────────────────────────────────────────

    def test_health_returns_ok(self, api_client):
        """/health endpoint returns 200 and {"status": "ok"}."""
        resp = api_client.get("/health")
        assert resp.status_code == 200
        assert resp.json() == {"status": "ok"}

    def test_rejects_non_pdf_extension(self, api_client):
        """Uploading a .txt file returns 400."""
        resp = api_client.post(
            "/analyse",
            files={"file": ("statement.txt", b"not a pdf", "text/plain")},
        )
        assert resp.status_code == 400
        assert "PDF" in resp.json()["detail"]

    def test_rejects_file_without_extension(self, api_client):
        """Uploading a file with no extension returns 400."""
        resp = api_client.post(
            "/analyse",
            files={"file": ("statement", b"not a pdf", "application/octet-stream")},
        )
        assert resp.status_code == 400

    def test_rejects_tiny_file(self, api_client):
        """Files under 1 KB are rejected with 400."""
        resp = api_client.post(
            "/analyse",
            files={"file": ("tiny.pdf", b"%PDF-1.4 tiny", "application/pdf")},
        )
        assert resp.status_code == 400

    def test_rejects_oversized_file(self, api_client):
        """Files over 15 MB are rejected with 413."""
        big_content = b"%PDF-1.4 " + b"x" * (15 * 1024 * 1024 + 1)
        resp = api_client.post(
            "/analyse",
            files={"file": ("big.pdf", big_content, "application/pdf")},
        )
        assert resp.status_code == 413

    def test_download_invalid_job_id(self, api_client):
        """Requesting a file with a short/invalid job_id returns 400."""
        resp = api_client.get("/files/not-a-valid-uuid/spending.csv")
        assert resp.status_code == 400

    def test_download_nonexistent_file(self, api_client):
        """Requesting a file that doesn't exist returns 404."""
        import uuid
        fake_id = str(uuid.uuid4())
        resp = api_client.get(f"/files/{fake_id}/spending_202603.csv")
        assert resp.status_code == 404

    def test_download_path_traversal_blocked(self, api_client):
        """Path traversal attempts in filename are rejected with 400."""
        import uuid
        fake_id = str(uuid.uuid4())
        resp = api_client.get(f"/files/{fake_id}/../../../etc/passwd")
        # FastAPI routing won't even match this (path param won't contain /)
        assert resp.status_code in (400, 404, 422)

    # ── slow test (calls real Groq API) ──────────────────────────────────────

    @pytest.mark.parametrize("pdf_path", _get_pdfs())
    def test_full_upload_flow(self, api_client, pdf_path):
        """
        Upload a real PDF → verify CSV + report URLs returned →
        download both files and verify they are valid.
        """
        if not _has_api_key():
            pytest.skip("API_KEY not set in backend/.env")

        with open(pdf_path, "rb") as f:
            resp = api_client.post(
                "/analyse",
                files={"file": (pdf_path.name, f, "application/pdf")},
            )

        assert resp.status_code == 200, (
            f"Upload failed for {pdf_path.name}: {resp.text}"
        )

        data = resp.json()
        assert "csv_url" in data,    "Response missing csv_url"
        assert "report_url" in data, "Response missing report_url"
        assert "row_count" in data,  "Response missing row_count"
        assert data["row_count"] > 0, "row_count is 0 — no transactions found"

        # Download CSV — strip /api prefix (added by Nginx; not in FastAPI routes)
        csv_url    = data["csv_url"].replace("/api/files/", "/files/")
        report_url = data["report_url"].replace("/api/files/", "/files/")

        csv_resp = api_client.get(csv_url)
        assert csv_resp.status_code == 200, f"CSV download failed: {csv_resp.status_code}"
        assert "Date" in csv_resp.text,     "CSV response missing Date column header"
        assert "Amount" in csv_resp.text,   "CSV response missing Amount column header"

        # Download PDF report
        pdf_resp = api_client.get(report_url)
        assert pdf_resp.status_code == 200, f"Report download failed: {pdf_resp.status_code}"
        assert pdf_resp.content[:4] == b"%PDF", "Downloaded report is not a valid PDF"
        assert len(pdf_resp.content) > 50_000, (
            f"Report PDF is only {len(pdf_resp.content)//1024} KB — looks empty"
        )
