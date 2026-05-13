# Backend Zero to Hero
### Learn Python backend development through your own Spending Analyser

---

> **How to use this book**
>
> Every example comes directly from this codebase. When you read about a concept,
> open the file mentioned and see it in action. The book grows with the project.
>
> Open this in VS Code preview: `Ctrl+Shift+V`

---

## Table of Contents

**Part I — The Foundation**
- [Chapter 1: What a Backend Does](#chapter-1-what-a-backend-does)
- [Chapter 2: The Tools We Use and Why](#chapter-2-the-tools-we-use-and-why)
- [Chapter 3: A Map of the Codebase](#chapter-3-a-map-of-the-codebase)

**Part II — Python You Need to Know**
- [Chapter 4: Python Essentials](#chapter-4-python-essentials)
- [Chapter 5: Files and Paths](#chapter-5-files-and-paths)
- [Chapter 6: Environment Variables and Config](#chapter-6-environment-variables-and-config)

**Part III — FastAPI**
- [Chapter 7: What is an API?](#chapter-7-what-is-an-api)
- [Chapter 8: FastAPI Basics](#chapter-8-fastapi-basics)
- [Chapter 9: File Uploads and Validation](#chapter-9-file-uploads-and-validation)
- [Chapter 10: Background Threads and Cleanup](#chapter-10-background-threads-and-cleanup)

**Part IV — AI Integration**
- [Chapter 11: Calling an AI API](#chapter-11-calling-an-ai-api)
- [Chapter 12: Vision AI — Reading PDFs as Images](#chapter-12-vision-ai--reading-pdfs-as-images)
- [Chapter 13: Rate Limiting and Retries](#chapter-13-rate-limiting-and-retries)

**Part V — Data Processing**
- [Chapter 14: Pandas — Working with Tabular Data](#chapter-14-pandas--working-with-tabular-data)
- [Chapter 15: The Categorization System](#chapter-15-the-categorization-system)
- [Chapter 16: Enriching the Dataset](#chapter-16-enriching-the-dataset)

**Part VI — PDF Report Generation**
- [Chapter 17: Matplotlib — Creating Charts](#chapter-17-matplotlib--creating-charts)
- [Chapter 18: Multi-Page PDF Reports](#chapter-18-multi-page-pdf-reports)

**Part VII — Production**
- [Chapter 19: Docker — Containerizing the App](#chapter-19-docker--containerizing-the-app)
- [Chapter 20: Nginx — The Gatekeeper](#chapter-20-nginx--the-gatekeeper)
- [Chapter 21: Testing with pytest](#chapter-21-testing-with-pytest)

**Appendix**
- [Glossary](#glossary)

---

# Part I — The Foundation

---

## Chapter 1: What a Backend Does

**What you'll understand after this chapter:**
The role of a backend in a web application, and how the frontend and backend of this project talk to each other.

---

### Frontend vs Backend

When you open souravspace.com, two separate systems are involved:

**Frontend (React)** — runs in your browser. Handles what you see and click. Cannot safely store secrets (like API keys) because anyone can view browser source code.

**Backend (FastAPI)** — runs on the server (your EC2 instance). Handles computation, file processing, calls to external APIs, and data storage. Hidden from users.

```
Your Browser                          EC2 Server
─────────────                         ──────────
React App                             FastAPI (app.py)
 ↓                                     ↓
Upload PDF  ──── HTTP POST /analyse ──→  Receives files
                                         Runs AI pipeline
                                         Generates report
            ←── JSON { csv_url, ... } ──  Returns URLs
 ↓
Download buttons appear
```

---

### What this backend specifically does

1. **Receives** PDF/Excel files uploaded from the browser
2. **Validates** them (correct format, not too large, not too many pages)
3. **Processes** them — renders each PDF page as an image, sends to a vision AI model, extracts transaction data
4. **Enriches** the data — adds 31 analytical columns (day of week, category, spend type, etc.)
5. **Generates** a 10-page PDF report with charts and AI insights
6. **Returns** download URLs for the CSV and report
7. **Cleans up** — deletes all files after 1 hour

---

### Why do we need a backend at all?

You might wonder: why not process everything in the browser?

- **API key security** — the Groq API key must not be visible to users. It lives only on the server.
- **Heavy computation** — rendering PDFs, calling an AI API 20 times, generating matplotlib charts — this needs server CPU, not a user's phone.
- **Library availability** — `PyMuPDF`, `pandas`, `matplotlib` are Python libraries. They don't run in a browser.

---

## Chapter 2: The Tools We Use and Why

**What you'll understand after this chapter:**
Every tool in the backend stack and why each one exists.

---

### Python

The programming language. Chosen because:
- Best ecosystem for data science: pandas, numpy, matplotlib
- First-class AI/ML libraries
- Clean syntax — readable even for newcomers
- FastAPI is Python-native

This project uses **Python 3.12** (specified in `pyproject.toml`).

---

### FastAPI

The web framework — it turns Python functions into HTTP endpoints.

Without FastAPI, you'd need to manually parse HTTP requests, handle routing, serialize responses to JSON, and much more. FastAPI does all of that. You write:

```python
@app.get("/health")
def health():
    return {"status": "ok"}
```

And FastAPI handles everything needed to make `GET /health` work over HTTP.

FastAPI was chosen over older frameworks (Flask, Django) because:
- **Async support** — handles multiple requests without blocking
- **Automatic validation** — checks types automatically
- **Auto-generated docs** — visit `/docs` to see all endpoints in a browser UI

---

### Uvicorn + Gunicorn

FastAPI itself is just Python code. You need a **server** to actually receive HTTP connections.

- **Uvicorn** — an ASGI server. Runs one instance of your app efficiently.
- **Gunicorn** — a process manager. Runs multiple Uvicorn workers (we use 2).

The Dockerfile's final command:
```bash
gunicorn app:app -w 2 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000 --timeout 1200
```

- `app:app` — the file `app.py`, the object named `app`
- `-w 2` — 2 worker processes
- `--bind 0.0.0.0:8000` — listen on port 8000 on all network interfaces
- `--timeout 1200` — 20 minutes before killing a stalled request (AI processing takes time)

---

### PyMuPDF (`fitz`)

A Python library for reading and rendering PDF files.

```python
import fitz

doc = fitz.open("statement.pdf")   # open the PDF
page = doc.load_page(0)            # get page 0 (first page)
pix = page.get_pixmap()            # render it as a pixel image
img_bytes = pix.tobytes("png")     # convert to PNG bytes
doc.close()
```

Used in `spending_pipeline.py` to render each PDF page as an image so the vision AI can read it.

---

### OpenAI SDK (talking to Groq)

The official OpenAI Python library — but we use it to talk to **Groq**, not OpenAI. Groq provides the same API interface as OpenAI, so the same library works.

```python
from openai import OpenAI

client = OpenAI(
    api_key="gsk_...",
    base_url="https://api.groq.com/openai/v1"   # ← Groq's URL
)
```

The model used is **Llama 4 Scout** — Meta's open-source vision model, running on Groq's fast inference hardware, free tier.

---

### Pandas

The go-to Python library for working with tabular data (like a spreadsheet in code).

```python
import pandas as pd

df = pd.DataFrame([
    {"Date": "2026-03-01", "Amount": 250.0, "Category": "Food"},
    {"Date": "2026-03-02", "Amount": 800.0, "Category": "Transport"},
])

print(df["Amount"].sum())    # → 1050.0
print(df[df["Category"] == "Food"])  # filter rows
```

Used in `spending_pipeline.py` to build the 31-column dataset and in `generate_report.py` to compute all chart data.

---

### Matplotlib

Python's standard chart library.

```python
import matplotlib.pyplot as plt

plt.bar(["Food", "Transport", "Shopping"], [5200, 1800, 3100])
plt.title("Spending by Category")
plt.savefig("chart.png")
```

Used in `generate_report.py` to draw all the charts (bar charts, donut charts, heatmaps, line charts) and save them to a PDF.

---

### Docker

Packages the entire app — Python, all libraries, the code — into one portable container. The same container runs identically on your laptop and on EC2.

Without Docker, deploying means manually installing Python 3.12, all 14 libraries, and configuring the system on every server. With Docker, one `docker pull` and `docker run` is enough.

---

### `uv`

A very fast Python package manager (replaces `pip`). Used instead of `pip install` because:
- 10-100x faster installs
- Deterministic: `uv sync --frozen` installs the exact versions in `uv.lock`, not "latest"
- Handles virtual environments automatically

---

### The stack in one diagram

```
Internet
  ↓
Nginx (port 80/443)       ← terminates SSL, serves React, rate-limits
  ↓
FastAPI / Uvicorn (port 8000)   ← your Python code
  ↓
Groq API (external)       ← vision AI (Llama 4 Scout)
```

---

## Chapter 3: A Map of the Codebase

**What you'll understand after this chapter:**
What every file does and where to look when you want to change something specific.

---

### Directory structure

```
backend/
└── budget-tracker/
    ├── app.py                 ← FastAPI server — HTTP endpoints, file handling, consent guard
    ├── spending_pipeline.py   ← Core engine — PDF parsing, categorization, enrichment
    ├── generate_report.py     ← Thin wrapper that calls report/orchestrator.py
    ├── data_loader.py         ← Pluggable data source (local disk / S3)
    ├── test_report.py         ← Unit + end-to-end tests for the report pipeline (30 tests)
    ├── test_integration.py    ← Integration tests (full API flow)
    ├── pyproject.toml         ← Python dependencies
    ├── uv.lock                ← Locked dependency versions (do not edit)
    ├── Dockerfile             ← Container build instructions
    ├── nginx.conf             ← Nginx reverse proxy config (two server blocks: HTTP + HTTPS)
    └── report/                ← PDF report package (one file per page / concern)
        ├── orchestrator.py    → Coordinates all 12 pages in order
        ├── scorer.py          → Algorithmic financial health score (6 components, 0-100)
        ├── recommender.py     → Rule-based recommendation engine (exact Rs. amounts)
        ├── ai_client.py       → Optional AI narrative enhancement (Groq)
        ├── theme.py           → Colors, fonts, chart helpers, arc gauge, gradient fill
        └── pages/
            ├── p00_cover.py   → Dark navy cover with arc gauge and KPI chips
            ├── p01_summary.py → Executive summary with stat cards and donut
            ├── p02_trends.py  → Daily + weekly spending trends
            ├── p03_categories.py → Category breakdown charts
            ├── p04_merchants.py  → Top merchants analysis
            ├── p05_spend_type.py → Essential vs discretionary + payment modes
            ├── p06_insights.py   → Key insight cards (10 insights)
            ├── p07_advanced.py   → Heatmap, cumulative curve, week-over-week
            ├── p08_cashflow.py   → Daily cash flow + top transactions table
            └── p09_advisor.py    → Score gauge, recommendations, budget targets (3 pages)
```

---

### What each file owns

| File | Responsibility |
|------|---------------|
| `app.py` | HTTP layer — receives requests, validates consent + files, orchestrates pipeline, returns responses |
| `spending_pipeline.py` | Intelligence — AI extraction, categorization, enrichment, deduplication |
| `generate_report.py` | Thin wrapper that calls `report/orchestrator.py` |
| `report/orchestrator.py` | Coordinates all 12 PDF pages in sequence |
| `report/scorer.py` | Algorithmic financial health score — 6 components, deterministic, 0-100 |
| `report/recommender.py` | Rule-based recommendations with exact Rs. amounts and percentages |
| `report/theme.py` | Chart style, color palette, arc gauge, gradient fill, page headers/footers |
| `report/pages/p00–p09` | One file per report page — isolated, independently editable |
| `data_loader.py` | Storage abstraction — local files or S3 |
| `test_report.py` | 30-test suite covering scorer, recommender, theme helpers, and end-to-end PDF generation |
| `test_integration.py` | Full API flow integration tests |
| `Dockerfile` | Packaging — how to build the container image |
| `nginx.conf` | Network — HTTP→HTTPS redirect, HTTPS with security headers, proxying, rate limiting |

---

### The data flow through the system

```
1. app.py           receives uploaded files, saves to /tmp/job-id/
2. app.py           calls spending_pipeline.detect_files()
3. spending_pipeline.parse_pdf_vision()  — renders pages, calls Groq
4. spending_pipeline.categorize_transaction()  — 150+ keyword rules
5. spending_pipeline.enrich_dataframe()  — adds 31 columns
6. app.py           saves CSV to /tmp/job-id/spending_YYYYMM.csv
7. generate_report.generate()  — reads CSV, draws charts, saves PDF
8. app.py           deletes source files, returns { csv_url, report_url }
9. cleanup thread   deletes the entire job folder after 1 hour
```

---

### When you want to change something, look here

| What to change | File |
|---------------|------|
| Add a new API endpoint | `app.py` |
| Add a new keyword to categorization | `spending_pipeline.py` — `CATEGORY_RULES` list |
| Add a new enrichment column | `spending_pipeline.py` — `enrich_dataframe()` function |
| Change a specific report page | `report/pages/p0N_name.py` — one file per page |
| Change report colors or fonts | `report/theme.py` — the `C` color dict and `apply_style()` |
| Change the financial scoring logic | `report/scorer.py` — one method per component |
| Add a new recommendation rule | `report/recommender.py` — `analyze()` method |
| Change max file size or page limit | `app.py` — config constants at the top |
| Change cleanup TTL (currently 1 hour) | `app.py` — `FILE_TTL_SECONDS` constant |
| Add a new dependency | `pyproject.toml` — then `uv sync` |
| Change how many CPU workers run | `Dockerfile` — `-w 2` in the CMD |
| Add or update security headers | `nginx.conf` — `add_header` lines inside the HTTPS server block |

---

# Part II — Python You Need to Know

---

## Chapter 4: Python Essentials

**What you'll understand after this chapter:**
The Python patterns used throughout this codebase. Not all of Python — just what you need.

---

### Variables and types

```python
# No type declaration needed — Python infers it
name    = "Sourav"          # str
amount  = 250.75            # float
count   = 12                # int
is_pdf  = True              # bool
files   = []                # list
config  = {}                # dict (key-value pairs)
nothing = None              # null equivalent
```

---

### f-strings — Python's template literals

```python
name  = "Sourav"
count = 5

# Old way
msg = "Hello " + name + ", you have " + str(count) + " files"

# f-string — just put an f before the quote, use {} for expressions
msg = f"Hello {name}, you have {count} files"
msg = f"Max size: {15 * 1024 * 1024} bytes"   # expressions work
```

Real example from `app.py`:

```python
raise HTTPException(413, f"'{fname}' is too large. Max {MAX_FILE_SIZE // (1024*1024)} MB.")
```

---

### Functions

```python
def greet(name):
    return f"Hello, {name}"

# Default parameters
def greet(name, formal=False):
    if formal:
        return f"Good day, {name}"
    return f"Hey {name}!"

greet("Sourav")            # → "Hey Sourav!"
greet("Sourav", True)      # → "Good day, Sourav"
greet("Sourav", formal=True)  # same, named argument
```

---

### Lists

```python
files = ["file1.pdf", "file2.pdf"]

files.append("file3.pdf")    # add to end
files[0]                     # "file1.pdf" — indexing
len(files)                   # 3 — count
"file1.pdf" in files         # True — membership check

# List comprehension — create a list from a loop
pdf_files = [f for f in files if f.endswith(".pdf")]
```

---

### Dictionaries

```python
transaction = {
    "Date":        "2026-03-15",
    "Amount":      250.0,
    "Description": "Swiggy",
    "Category":    "Food & Dining",
}

transaction["Amount"]          # 250.0 — access
transaction["Type"] = "Debit"  # add new key
transaction.get("UPI_ID", "")  # safe access with default
```

---

### Loops

```python
# for loop — iterate over items
for file in files:
    print(file)

# Loop with index
for i, file in enumerate(files):
    print(f"File {i}: {file}")

# Loop over dict
for key, value in transaction.items():
    print(f"{key}: {value}")

# Range
for attempt in range(6):     # 0, 1, 2, 3, 4, 5
    print(attempt)
```

---

### Conditionals

```python
if amount > 1000:
    category = "Major"
elif amount > 200:
    category = "Medium"
else:
    category = "Small"

# Inline (ternary)
txn_type = "Credit" if raw_type == "credit" else "Debit"

# `in` check
if "SWIGGY" in description.upper():
    category = "Food & Dining"
```

---

### `try` / `except` — error handling

```python
try:
    amount = float("123.45")   # might fail if string isn't a number
    doc = fitz.open(pdf_path)  # might fail if file is corrupt
except ValueError:
    amount = 0
except Exception as e:
    print(f"Error: {e}")
    return []
```

Real example from `spending_pipeline.py` — parsing amounts:

```python
try:
    amount = float(
        str(txn["amount"])
        .replace(",", "")      # remove "1,234" → "1234"
        .replace("Rs.", "")    # remove "Rs.250" → "250"
        .replace("INR", "")
        .strip()
    )
except (ValueError, TypeError):
    continue    # skip this transaction if amount can't be parsed
```

---

### `continue` and `break` in loops

```python
for txn in page_txns:
    if amount <= 0:
        continue    # skip to next iteration
    if len(transactions) > 1000:
        break       # exit the loop entirely
    transactions.append(txn)
```

---

### Classes and objects

Python uses classes to bundle related data and functions. You don't need to write many classes in this codebase, but you'll read them.

```python
class DataLoader:
    def load(self, folder):
        raise NotImplementedError  # subclasses must implement this

class LocalDataLoader(DataLoader):
    def load(self, folder):
        return os.listdir(folder)  # concrete implementation
```

`data_loader.py` uses this pattern (called the **Strategy pattern**) — swapping `LocalDataLoader` for `S3DataLoader` changes where files come from without changing any other code.

---

### `with` statement — automatic cleanup

The `with` statement ensures cleanup happens even if an error occurs:

```python
# Without with — must manually close
doc = fitz.open("statement.pdf")
# ... use doc ...
doc.close()   # what if an error happens above? close() never called!

# With with — close() is called automatically
with fitz.open("statement.pdf") as doc:
    page = doc.load_page(0)
# doc is automatically closed here, even if an error occurred
```

---

### List comprehensions and generators

```python
# Regular loop
pdfs = []
for f in all_files:
    if f.endswith(".pdf"):
        pdfs.append(f)

# List comprehension — same thing, one line
pdfs = [f for f in all_files if f.endswith(".pdf")]

# With transformation
lower_names = [f.lower() for f in all_files]
```

Real example from `spending_pipeline.py`:

```python
# Find the most common year across all transactions
years = [t["Date"].year for t in transactions]
mode_year = max(set(years), key=years.count)
```

---

### `any()` and `all()`

```python
# any() — True if at least one item is True
has_pdf = any(f.endswith(".pdf") for f in files)

# all() — True if every item is True
all_valid = all(len(f) > 2 for f in descriptions)
```

Real example from `spending_pipeline.py` — checking required fields:

```python
if not all(k in txn for k in ("date", "description", "amount", "type")):
    continue   # skip transaction if any required field is missing
```

---

## Chapter 5: Files and Paths

**What you'll understand after this chapter:**
How Python reads, writes, and navigates files — used everywhere in this codebase.

---

### `pathlib.Path` — the modern way to work with files

```python
from pathlib import Path

p = Path("/var/lib/spending-api/files")

p.mkdir(parents=True, exist_ok=True)   # create directory (and parents)
p.exists()          # True/False — does it exist?
p.is_dir()          # True if it's a directory
p.is_file()         # True if it's a file

# Building paths — / operator joins path components
job_dir = p / "abc-123-uuid"         # /var/lib/.../files/abc-123-uuid
csv_path = job_dir / "spending.csv"  # /var/lib/.../files/abc-123-uuid/spending.csv

csv_path.name       # "spending.csv" — filename only
csv_path.suffix     # ".csv" — extension
csv_path.stem       # "spending" — filename without extension

# Reading and writing
csv_path.write_bytes(content)   # write raw bytes
csv_path.write_text("hello")    # write a string
csv_path.read_bytes()           # read raw bytes
csv_path.read_text()            # read as string

# Deleting
csv_path.unlink(missing_ok=True)  # delete (no error if doesn't exist)
```

Real example from `app.py`:

```python
FILES_DIR = Path(os.environ.get("FILES_DIR", "/var/lib/spending-api/files"))
FILES_DIR.mkdir(parents=True, exist_ok=True)   # create on startup if needed

job_id  = str(uuid.uuid4())           # "550e8400-e29b-41d4-a716-446655440000"
job_dir = FILES_DIR / job_id          # unique folder per request
job_dir.mkdir()

dest = job_dir / fname                # save each file inside the job folder
dest.write_bytes(content)
```

---

### Iterating a directory

```python
for item in FILES_DIR.iterdir():
    if item.is_dir():
        age = time.time() - item.stat().st_mtime   # seconds since last modified
        if age > 3600:
            shutil.rmtree(item)   # delete the folder and everything inside
```

---

### `os.path` — the older (but still used) approach

```python
import os

os.path.join("/var", "lib", "files")    # "/var/lib/files"
os.path.basename("/var/lib/file.pdf")   # "file.pdf"
os.path.splitext("file.pdf")            # ("file", ".pdf")
os.path.exists("/var/lib/files")        # True/False
os.makedirs("/var/lib/files", exist_ok=True)
```

`spending_pipeline.py` uses `os.path` (older style). `app.py` uses `pathlib.Path` (newer). Both are valid — you'll see both in the wild.

---

### UUID — unique job IDs

```python
import uuid

job_id = str(uuid.uuid4())
# → "550e8400-e29b-41d4-a716-446655440000"
# 32 hex digits + 4 dashes = 36 characters
# Statistically impossible to collide across requests
```

Each upload creates a unique folder using a UUID. This prevents two simultaneous requests from overwriting each other's files.

---

## Chapter 6: Environment Variables and Config

**What you'll understand after this chapter:**
How the app reads its configuration from environment variables — not from hardcoded values.

---

### Why environment variables?

Hardcoding secrets in code is dangerous:

```python
# NEVER do this
API_KEY = "gsk_abc123xyz"   # this gets committed to GitHub, exposed publicly
```

Environment variables are set in the server's environment, not in code:

```bash
# On EC2, when starting the Docker container:
docker run -e API_KEY=gsk_abc123xyz ...
```

The code reads them:

```python
import os

api_key = os.environ.get("API_KEY")
```

No secret in the code. The code is safe to push to GitHub.

---

### `python-dotenv` — loading from a `.env` file

For local development, typing `export API_KEY=...` in the terminal every time is tedious. A `.env` file stores them:

```bash
# .env file (never commit this to git)
API_KEY=gsk_abc123xyz
BASE_URL=https://api.groq.com/openai/v1
MODEL=meta-llama/llama-4-scout-17b-16e-instruct
FILES_DIR=/tmp/spending-files
```

In Python:

```python
from dotenv import load_dotenv
load_dotenv()   # reads .env and loads values into os.environ

api_key = os.environ.get("API_KEY")   # works now
```

`load_dotenv()` is called at the top of both `app.py` and `spending_pipeline.py`.

---

### Config constants in `app.py`

All configurable values are collected at the top of the file as named constants:

```python
FILES_DIR        = Path(os.environ.get("FILES_DIR", "/var/lib/spending-api/files"))
ALLOWED_ORIGINS  = [o.strip() for o in os.environ.get("ALLOWED_ORIGINS", "*").split(",")]
MAX_FILE_SIZE    = 15 * 1024 * 1024   # 15 MB in bytes
MAX_PDF_PAGES    = 50
FILE_TTL_SECONDS = 3600               # 1 hour
```

**Why name them at the top?**
- Easy to find and change
- No magic numbers scattered through the code
- `os.environ.get("FILES_DIR", "/var/lib/spending-api/files")` — the second argument is the default value if the env var isn't set

---

# Part III — FastAPI

---

## Chapter 7: What is an API?

**What you'll understand after this chapter:**
What an API is, what HTTP methods mean, and how the browser and server communicate.

---

### API — Application Programming Interface

An API is a contract between two programs. The server defines:
- Which URLs it listens to
- What data it expects
- What data it returns

The browser (client) follows that contract.

---

### HTTP Methods

Every request has a method that describes the intent:

| Method | Meaning | Example use |
|--------|---------|-------------|
| `GET` | Fetch data, no side effects | `/health`, `/files/abc/report.pdf` |
| `POST` | Submit data, create something | `/analyse` (upload files) |
| `PUT` | Replace an entire resource | Update a profile |
| `DELETE` | Remove something | Delete a job |

Our API only uses `GET` and `POST`.

---

### HTTP Status Codes

Every response has a numeric status code:

| Code | Meaning | When we use it |
|------|---------|---------------|
| `200` | OK | Successful GET or POST |
| `400` | Bad Request | Invalid file type, missing files |
| `404` | Not Found | File expired or wrong job ID |
| `413` | Payload Too Large | File exceeds 15 MB |
| `500` | Internal Server Error | Unexpected crash in the pipeline |

---

### Request → Response cycle

```
Browser                          Server (FastAPI)
──────                           ───────────────
POST /analyse                  →
  headers: Content-Type: multipart/form-data
  body: [file1.pdf bytes] [file2.pdf bytes]

                               ← 200 OK
                                  body: {
                                    "csv_url": "/files/abc/spending.csv",
                                    "report_url": "/files/abc/report.pdf",
                                    "row_count": 143
                                  }
```

The browser's `fetch()` call (in `SpendingTool.jsx`) sends this request. FastAPI's `@app.post("/analyse")` receives it.

---

## Chapter 8: FastAPI Basics

**What you'll understand after this chapter:**
How to define routes, return responses, raise errors, and add middleware.

---

### Creating the app

```python
from fastapi import FastAPI

app = FastAPI(title="Spending Analyser")
```

`app` is the FastAPI application object. Every route is registered on it.

---

### Defining routes

A **route** is a function that handles a specific URL + method combination:

```python
@app.get("/health")           # ← decorator: method + path
def health():                 # ← the handler function
    return {"status": "ok"}   # ← return a dict → FastAPI converts to JSON
```

`@app.get` is a decorator — it registers the function as the handler for `GET /health`.

```python
@app.post("/analyse")
async def analyse(request: Request, files: List[UploadFile] = File(...)):
    # handles POST /analyse
    ...
```

`async def` — this function can be paused to wait for I/O (network, file reads) without blocking other requests. `async` + `await` is covered below.

---

### Returning responses

Return a Python dict → FastAPI automatically converts to JSON:

```python
return {
    "csv_url":    f"/files/{job_id}/{csv_name}",
    "report_url": f"/files/{job_id}/{report_name}",
    "row_count":  len(df),
}
```

Return a file:

```python
from fastapi.responses import FileResponse

return FileResponse(path, filename=filename, media_type="application/pdf")
```

---

### Raising errors

```python
from fastapi import HTTPException

raise HTTPException(400, "No files provided.")
raise HTTPException(413, f"'{fname}' is too large. Max 15 MB.")
raise HTTPException(404, "File not found or expired.")
raise HTTPException(500, f"Processing failed: {e}")
```

FastAPI catches these and returns the appropriate HTTP status code with a JSON body:

```json
{ "detail": "No files provided." }
```

The frontend's `SpendingTool.jsx` reads `err.detail` from the response.

---

### `async` / `await` in FastAPI

```python
@app.post("/analyse")
async def analyse(files: List[UploadFile] = File(...)):
    content = await upload.read()   # read file bytes without blocking
    ...
```

`await` pauses the function until the awaited operation completes, but the server can handle other requests in the meantime. Think of it as: "go do something else while this I/O operation is running."

Use `async def` + `await` for: reading files, HTTP calls, database queries.
Use regular `def` for: CPU-heavy work (our pipeline is CPU-heavy, so the pipeline runs in a synchronous endpoint).

---

### CORS middleware

Browsers block JavaScript from calling APIs on different domains by default (security feature called Same-Origin Policy). CORS (Cross-Origin Resource Sharing) headers tell the browser which origins are allowed.

```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://souravspace.com"],  # who can call this API
    allow_origin_regex=r"http://localhost:\d+", # also allow local dev
    allow_credentials=False,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)
```

Without this, the browser would refuse to show the API response even if the server sent it correctly.

---

### Path parameters

```python
@app.get("/files/{job_id}/{filename}")
def download(job_id: str, filename: str):
    # job_id and filename come from the URL path
    path = FILES_DIR / job_id / filename
    ...
```

`/files/abc-123/report.pdf` → `job_id = "abc-123"`, `filename = "report.pdf"`.

---

## Chapter 9: File Uploads and Validation

**What you'll understand after this chapter:**
How multipart file uploads work, and the multi-layer validation strategy in this app.

---

### Receiving uploaded files

```python
from fastapi import File, UploadFile
from typing import List

@app.post("/analyse")
async def analyse(files: List[UploadFile] = File(...)):
    for upload in files:
        fname   = upload.filename      # "statement.pdf"
        content = await upload.read()  # raw bytes of the file
```

`List[UploadFile]` means "expect one or more uploaded files". The browser sends them as `multipart/form-data` — the same format as an HTML `<form>` with `enctype="multipart/form-data"`.

---

### The validation layers

The app validates files in five stages, starting with consent:

**Layer 0 — Consent header check (privacy compliance):**

```python
consent = request.headers.get("X-Consent-Given", "").strip().lower()
if consent != "true":
    raise HTTPException(400, "Consent not provided. Please accept the data processing terms before uploading.")
```

This is the very first check — before touching any uploaded file. The frontend (`SpendingTool.jsx`) sends `X-Consent-Given: true` only after the user ticks all three checkboxes in `ConsentModal.jsx`. If the header is absent or anything other than `"true"`, the server refuses with a 400 error.

Why enforce this server-side rather than trusting the frontend? Because the frontend can be bypassed — someone could use `curl` or Postman to call the API directly. The server-side check ensures that **no bank statement is ever processed without documented consent**, regardless of how the request was made.

**Layer 1 — Extension check:**

```python
fname_lower = fname.lower()
is_pdf   = fname_lower.endswith(".pdf")
is_sheet = fname_lower.endswith((".xlsx", ".xls", ".csv"))

if not is_pdf and not is_sheet:
    raise HTTPException(400, f"'{fname}': only PDF, Excel, or CSV files are accepted.")
```

**Layer 2 — Size check:**

```python
MAX_FILE_SIZE = 15 * 1024 * 1024   # 15 MB

content = await upload.read()
if len(content) > MAX_FILE_SIZE:
    raise HTTPException(413, f"'{fname}' is too large. Max {MAX_FILE_SIZE // (1024*1024)} MB.")
if len(content) < 100:
    raise HTTPException(400, f"'{fname}' appears to be empty.")
```

`len(content)` on bytes returns the number of bytes. `15 * 1024 * 1024` = 15 MB.

**Layer 3 — PDF page count (cost protection):**

```python
import fitz

for src in saved_sources:
    if src.suffix.lower() == ".pdf":
        doc = fitz.open(src)
        n_pages = len(doc)
        doc.close()
        if n_pages > MAX_PDF_PAGES:
            raise HTTPException(400, f"'{src.name}' has {n_pages} pages — max 50 allowed.")
```

Each PDF page requires one Groq API call. 50 pages = 50 calls. This protects against someone uploading a 500-page PDF that would exhaust the free API quota.

**Layer 4 — Path traversal protection (security):**

```python
@app.get("/files/{job_id}/{filename}")
def download(job_id: str, filename: str):
    if len(job_id) != 36:
        raise HTTPException(400, "Invalid job_id.")
    if "/" in filename or ".." in filename or "\\" in filename:
        raise HTTPException(400, "Invalid filename.")
```

A malicious user could send `filename = "../../../etc/passwd"` to read any file on the server. Checking for `/`, `..`, and `\` blocks this attack.

---

### Job isolation

Every upload gets its own UUID-based directory:

```python
job_id  = str(uuid.uuid4())    # unique per request
job_dir = FILES_DIR / job_id   # /tmp/spending-files/550e8400-.../
job_dir.mkdir()
```

This means:
- Two simultaneous uploads never interfere with each other
- The download URL encodes both the job and filename: `/files/{job_id}/{filename}`
- Cleanup is simple: delete the whole job directory

---

### File permission hardening

After creating the job directory and writing output files, restrictive Unix permissions are set:

```python
job_dir.mkdir()
os.chmod(job_dir, 0o700)   # owner can read/write/enter; no one else can list the directory

# ... after saving the CSV:
os.chmod(csv_path, 0o600)  # owner read/write only

# ... after generating the PDF:
os.chmod(report_path, 0o600)
```

`0o700` and `0o600` are **octal permission notation** (the `0o` prefix means base-8):

```
0o700  →  rwx------   directory: owner can read, write, enter; group and others: nothing
0o600  →  rw-------   file:      owner can read and write; group and others: nothing
```

This matters on a shared server. Without these, the default umask might make files readable by the web server process group or other users on the system.

**On Windows (your dev machine):** `os.chmod` with Unix permission bits is a no-op — Windows has a different permission model (`icacls`). These calls are harmless but do nothing locally. They only take effect on the Linux EC2 instance.

---

### Cleanup after success

```python
# After generating CSV and report, delete the uploaded source PDFs
for src in saved_sources:
    src.unlink(missing_ok=True)
```

Users' bank statements are deleted immediately after processing. Only the CSV and report remain (for 1 hour).

---

## Chapter 10: Background Threads and Cleanup

**What you'll understand after this chapter:**
How to run code in the background on a timer, and why this pattern is used for file cleanup.

---

### The problem

Job directories accumulate over time. If a user downloads their report and leaves, the directory sits on disk forever. After 1 hour, we want it gone.

Options:
1. Delete on next request — messy, not reliable
2. A scheduled job (cron) — works, but needs extra setup
3. **A background thread** — runs inside the app, simple, always running

---

### The cleanup loop

```python
import time
import shutil
from threading import Thread

def _cleanup_loop():
    while True:
        try:
            now = time.time()
            for job_dir in FILES_DIR.iterdir():
                if job_dir.is_dir() and (now - job_dir.stat().st_mtime) > FILE_TTL_SECONDS:
                    shutil.rmtree(job_dir, ignore_errors=True)
        except Exception:
            pass  # never crash the cleanup loop
        time.sleep(300)  # wait 5 minutes, then check again
```

Step by step:
1. `while True` — runs forever
2. `time.time()` — current time in seconds (Unix timestamp)
3. `job_dir.stat().st_mtime` — when the directory was last modified
4. If older than `FILE_TTL_SECONDS` (3600 = 1 hour), delete with `shutil.rmtree`
5. `time.sleep(300)` — pause 5 minutes before the next scan

---

### Starting the thread

```python
Thread(target=_cleanup_loop, daemon=True).start()
```

- `target=_cleanup_loop` — run this function
- `daemon=True` — when the main app shuts down, this thread also shuts down automatically (not a daemon thread would keep the process alive)
- `.start()` — launch it in the background

This runs once when `app.py` is imported — the cleanup thread starts when the server starts.

---

### Why wrap the loop in `try/except`?

```python
try:
    # cleanup logic
except Exception:
    pass
```

If an unexpected error occurs (permissions issue, race condition), `pass` silently ignores it. The `while True` loop continues on the next iteration. A cleanup thread should never crash the server.

---

# Part IV — AI Integration

---

## Chapter 11: Calling an AI API

**What you'll understand after this chapter:**
How to make calls to an LLM API from Python, and how to structure prompts for reliable structured output.

---

### Setting up the client

```python
from openai import OpenAI
import os

client = OpenAI(
    api_key=os.environ.get("API_KEY"),
    base_url="https://api.groq.com/openai/v1"   # Groq's API is OpenAI-compatible
)
```

`base_url` overrides where the client sends requests. Groq's API uses the exact same format as OpenAI — so the same library works for both.

---

### Making a chat completion call

```python
response = client.chat.completions.create(
    model="meta-llama/llama-4-scout-17b-16e-instruct",
    temperature=0,
    response_format={"type": "json_object"},   # force JSON output
    messages=[
        {"role": "system", "content": "You are a financial data extractor..."},
        {"role": "user",   "content": "Extract transactions from this image."},
    ]
)

result = response.choices[0].message.content   # the model's reply as a string
```

**`temperature=0`** — makes the model deterministic. For data extraction, you want consistent results, not creative variation.

**`response_format={"type": "json_object"}`** — forces the model to return valid JSON. Without this, the model might add "Here is the JSON:" or other text around it, breaking `json.loads()`.

---

### Parsing the response

```python
import json

raw = response.choices[0].message.content
# → '{"transactions": [{"date": "15/03/2026", "amount": 250, ...}]}'

data = json.loads(raw)
transactions = data.get("transactions", [])
```

`json.loads()` converts a JSON string to a Python dict/list.

---

### Structuring prompts for reliable extraction

The `VISION_PROMPT` in `spending_pipeline.py` is carefully crafted:

```python
VISION_PROMPT = """You are a financial transaction extractor reading a bank statement page image.

TASK: Extract every individual transaction row visible on this page.

Return ONLY valid JSON — no markdown, no explanation:
{"transactions":[{"date":"DD/MM/YYYY","time":"HH:MM or empty","description":"...","amount":123.45,"type":"Debit or Credit"}]}

=== CLASSIFICATION RULES ===

CREDIT CARD statements:
- Purchase / Fee / Interest / EMI charge  → type = "Debit"
...
"""
```

**Why the prompt is so specific:**
- "Return ONLY valid JSON" — prevents the model from adding prose around the JSON
- Exact format specification — models hallucinate less when given a concrete example
- Explicit rules per bank type — credit card "payments" should be "Transfer", not "Debit"
- What NOT to include (opening balance, closing balance rows) — prevents false positives

Good prompts are the difference between a pipeline that works and one that requires manual cleanup.

---

## Chapter 12: Vision AI — Reading PDFs as Images

**What you'll understand after this chapter:**
Why we render PDFs as images instead of extracting text, and how each page gets sent to the model.

---

### Why images, not text?

The naive approach to reading a PDF is extracting its text layer:

```python
doc = fitz.open("statement.pdf")
text = doc[0].get_text()   # extract all text
```

This works for simple PDFs but breaks on:
- Scanned PDFs (no text layer at all — just a photo of a document)
- PDFs with complex column layouts (text extraction scrambles the order)
- PDFs where amounts and descriptions are in different visual columns

**Vision AI reads the page the same way a human does** — as a picture. It understands spatial layout, can read tables, and handles any bank's formatting.

---

### Rendering a PDF page to an image

```python
import fitz      # PyMuPDF
import base64

doc  = fitz.open(pdf_path)
page = doc.load_page(0)              # page index 0 = first page

# Render the page as a pixel image at 1x zoom
mat = fitz.Matrix(1.0, 1.0)         # zoom factor (1.0 = original size)
pix = page.get_pixmap(matrix=mat, alpha=False)  # no transparency needed

# Convert to PNG bytes, then to base64 string
img_bytes = pix.tobytes("png")
img_b64   = base64.b64encode(img_bytes).decode()

doc.close()
```

**`base64`** — binary data (like an image) can't be sent directly in a JSON string. Base64 encodes it as a string of letters and numbers.

---

### Sending the image to the API

```python
messages = [
    {"role": "system", "content": VISION_PROMPT},
    {"role": "user",   "content": [
        {"type": "text",      "text": context},
        {"type": "image_url", "image_url": {
            "url":    f"data:image/png;base64,{img_b64}",
            "detail": "high",
        }},
    ]},
]
```

The `data:image/png;base64,{img_b64}` format is a **data URL** — it embeds the image directly in the string instead of linking to a URL. The model receives the image as part of the message.

**`"detail": "high"`** — tells the model to process the image at full resolution, not a compressed thumbnail.

---

### Processing multiple pages

```python
n_pages = len(doc)

for page_num in range(n_pages):
    if page_num > 0:
        time.sleep(25)   # pace calls to stay under Groq's rate limit
    
    page = doc.load_page(page_num)
    # ... render, encode, send to API ...
```

A 10-page bank statement = 10 API calls. The `time.sleep(25)` between pages stays under Groq's free tier token-per-minute limit.

---

## Chapter 13: Rate Limiting and Retries

**What you'll understand after this chapter:**
What API rate limits are and how the exponential backoff strategy handles them gracefully.

---

### What is rate limiting?

Groq (like most APIs) limits how many requests you can make per minute. If you exceed the limit, the API returns a `429 Too Many Requests` error.

Free tier limit: a certain number of tokens per minute. Large PDFs push against this.

---

### Exponential backoff

When we hit a rate limit, we wait and retry. The wait time grows exponentially with each failure:

```
Attempt 1 fails → wait 2s
Attempt 2 fails → wait 4s
Attempt 3 fails → wait 8s
Attempt 4 fails → wait 16s
Attempt 5 fails → wait 32s (capped at 60s)
```

Real code from `spending_pipeline.py`:

```python
for attempt in range(6):   # try up to 6 times
    try:
        raw = _call_vision(client, model, img_b64, VISION_PROMPT, context)
        break   # success — exit the retry loop
    except Exception as e:
        err = str(e)
        if "429" in err or "rate_limit" in err.lower():
            wait = _parse_retry_after(err) or min(2 ** (attempt + 1), 60)
            #                                    ↑ 2, 4, 8, 16, 32, 60 (capped)
            print(f"Page {page_num + 1}: rate limit, retrying in {wait}s...")
            time.sleep(wait)
        else:
            print(f"Page {page_num + 1}: error — {e}")
            break   # non-rate-limit error, stop retrying
```

---

### Parsing the `retry-after` header

Groq's error message says "Please try again in 1m 30.5s". We parse this:

```python
def _parse_retry_after(err_str):
    m = re.search(r'try again in (?:(\d+)m)?(\d+(?:\.\d+)?)s', err_str)
    #                             ↑ optional minutes   ↑ seconds
    if m:
        minutes = int(m.group(1)) if m.group(1) else 0
        return int(float(m.group(2)) + minutes * 60) + 5  # +5s buffer
    return None   # if parsing fails, use exponential backoff
```

`re.search()` searches a string for a pattern. `r'...'` is a raw string (backslashes are literal, not escape sequences). This is a **regular expression** — a mini-language for text pattern matching.

---

# Part V — Data Processing

---

## Chapter 14: Pandas — Working with Tabular Data

**What you'll understand after this chapter:**
How pandas DataFrames work and the core operations used in this codebase.

---

### What is a DataFrame?

A DataFrame is a table — rows and columns, like a spreadsheet, but in Python memory.

```python
import pandas as pd

df = pd.DataFrame([
    {"Date": "2026-03-01", "Amount": 250.0, "Category": "Food"},
    {"Date": "2026-03-02", "Amount": 800.0, "Category": "Transport"},
    {"Date": "2026-03-03", "Amount": 500.0, "Category": "Food"},
])

print(df)
#         Date  Amount   Category
# 0  2026-03-01   250.0       Food
# 1  2026-03-02   800.0  Transport
# 2  2026-03-03   500.0       Food
```

---

### Creating a DataFrame from a list of dicts

This is exactly how the pipeline works:

```python
all_transactions = [
    {"Date": datetime(...), "Amount": 250.0, "Description": "Swiggy", ...},
    {"Date": datetime(...), "Amount": 800.0, "Description": "Rapido", ...},
]

df = pd.DataFrame(all_transactions)
# Each dict becomes a row. Keys become column names.
```

---

### Selecting columns and rows

```python
df["Amount"]              # select one column → Series
df[["Amount", "Category"]]  # select multiple columns → DataFrame

df[df["Type"] == "Debit"]         # filter rows where Type is Debit
df[df["Amount"] > 1000]           # filter rows where Amount > 1000

debits = df[df["Type"] == "Debit"]
total_spent = debits["Amount"].sum()   # sum the Amount column
```

---

### Adding new columns

```python
# From a direct calculation
df["Is_Debit"] = (df["Type"] == "Debit").astype(int)
#                 ↑ boolean Series           ↑ convert True/False to 1/0

# From a function applied to each row
df["Amount_Bucket"] = df["Amount"].apply(amount_bucket)
#                                        ↑ called once per row
```

---

### Date handling

```python
df["Date"] = pd.to_datetime(df["Date"])   # convert strings to datetime objects

df["Day"]          = df["Date"].dt.day          # day number (1-31)
df["Day_Name"]     = df["Date"].dt.day_name()   # "Monday", "Tuesday", etc.
df["Month"]        = df["Date"].dt.month        # month number (1-12)
df["Month_Name"]   = df["Date"].dt.strftime("%B")  # "January", "February"
df["Year"]         = df["Date"].dt.year
df["Is_Weekend"]   = df["Date"].dt.dayofweek.isin([5, 6])  # Sat=5, Sun=6
```

---

### GroupBy — aggregate by category

```python
# Total spent per category
cat_totals = df.groupby("Category")["Amount"].sum()
#              ↑ group rows by     ↑ which column  ↑ operation
# → Series: Category → total Amount

# Sort descending
cat_totals = cat_totals.sort_values(ascending=False)

# Top 5 categories
top5 = cat_totals.head(5)
```

---

### Saving and loading

```python
# Save to CSV
df.to_csv("spending_202603.csv", index=False, encoding="utf-8-sig")
# index=False — don't write the row numbers
# utf-8-sig — Excel-compatible UTF-8 with BOM (for Hindi/special chars)

# Load from CSV
df = pd.read_csv("spending_202603.csv")

# Load from Excel
df = pd.read_excel("transactions.xlsx")
```

---

## Chapter 15: The Categorization System

**What you'll understand after this chapter:**
How the rule-based keyword categorizer works and how to extend it.

---

### The `CATEGORY_RULES` list

```python
CATEGORY_RULES = [
    ("SWIGGY FOOD",        "Food & Dining",  "Swiggy Food"),
    ("SWIGGY INSTAMART",   "Groceries",      "Swiggy Instamart"),
    ("SWIGGY",             "Food & Dining",  "Swiggy"),
    ("RAPIDO",             "Transport",      "Rapido"),
    ("NETFLIX",            "Subscriptions",  "Netflix"),
    # ... 150+ more rules
]
```

Each rule is a tuple of three strings:
1. **Keyword** — what to look for in the description (uppercase)
2. **Category** — the main category
3. **Subcategory** — the specific label

**Rule order matters**: "SWIGGY FOOD" comes before "SWIGGY" because the matching is first-match-wins. If "SWIGGY" came first, Swiggy Food orders would be miscategorized as generic "Swiggy".

---

### The `categorize_transaction` function

```python
def categorize_transaction(description):
    desc_upper = description.upper()       # normalise to uppercase
    for keyword, category, subcategory in CATEGORY_RULES:
        if keyword.upper() in desc_upper:  # check if keyword is anywhere in description
            return category, subcategory
    return "Uncategorized", "Other"        # default if no rule matched
```

This is a simple linear scan through the rules list. For 150 rules and thousands of transactions, this is fast enough.

**Why `upper()`?** The description might be "swiggy" or "SWIGGY" or "Swiggy" — converting both to uppercase before comparing handles all cases.

---

### Adding a new category rule

To add "BIGBAZAAR" as Groceries, add one line to `CATEGORY_RULES`:

```python
CATEGORY_RULES = [
    ...
    ("BIGBAZAAR",   "Groceries",  "Big Bazaar"),   # ← add here
    ...
]
```

The position matters — add it before any broader keyword that might match first.

---

### Post-processing overrides

After the keyword match, the code applies logic-based overrides:

```python
# Auto-fix based on description keywords
if any(w in desc_up for w in ("CASHBACK", "REFUND", "REWARD", "REVERSAL")):
    txn_type = "Credit"
elif any(w in desc_up for w in ("NEFT", "IMPS", "RTGS")) and is_cc:
    txn_type = "Transfer"   # card payment, not a purchase
```

And type-based overrides:

```python
# After we know the type:
if txn_type == "Credit":
    if any(w in desc_up for w in ("CASHBACK", "REWARD")):
        category, subcategory = "Cashback/Rewards", "Cashback"
```

This layered approach handles edge cases that a simple keyword match can't.

---

## Chapter 16: Enriching the Dataset

**What you'll understand after this chapter:**
How raw transactions become a 31-column Power BI-ready dataset.

---

### Why enrich?

The AI extracts bare minimum data: date, description, amount, type. But for analysis you want:
- Was it a weekend? (buying patterns differ)
- What time of day?
- What's the running total?
- Is it a recurring subscription?
- Essential or discretionary?

The `enrich_dataframe()` function adds all of this.

---

### Time columns from a date

```python
df["Date"] = pd.to_datetime(df["Date"])   # ensure proper datetime type

df["Day"]         = df["Date"].dt.day          # 1–31
df["Day_Name"]    = df["Date"].dt.day_name()   # "Monday"
df["Day_of_Week"] = df["Date"].dt.dayofweek    # 0=Mon, 6=Sun
df["Week_Number"] = df["Date"].dt.isocalendar().week.astype(int)
df["Month"]       = df["Date"].dt.month
df["Month_Name"]  = df["Date"].dt.strftime("%B")   # "March"
df["Year"]        = df["Date"].dt.year
df["Quarter"]     = df["Date"].dt.quarter          # 1–4
df["Year_Month"]  = df["Date"].dt.strftime("%Y-%m") # "2026-03"
df["Is_Weekend"]  = df["Date"].dt.dayofweek.isin([5, 6]).map({True: "Yes", False: "No"})
```

---

### Bucketing amounts

```python
def amount_bucket(a):
    if a <=    50: return "Rs.0-50 (Micro)"
    if a <=   200: return "Rs.51-200 (Small)"
    if a <=   500: return "Rs.201-500 (Medium)"
    if a <=  1000: return "Rs.501-1000 (Large)"
    if a <=  5000: return "Rs.1001-5000 (Major)"
    return "Rs.5000+ (Mega)"

df["Amount_Bucket"] = df["Amount"].apply(amount_bucket)
```

`apply()` calls the function once for each value in the column.

---

### Recurring subscription detection

```python
recurring_kw = [
    "NETFLIX", "SPOTIFY", "CLAUDE", "JIO", "AIRTEL",
    "RENT", "FLAT OWNER", "EMI", "HOTSTAR", "PRIME VIDEO",
]

df["Is_Recurring"] = df["Description"].apply(
    lambda d: "Yes" if any(k in d.upper() for k in recurring_kw) else "No"
)
```

`lambda` is a small inline function: `lambda d: ...` is equivalent to `def f(d): return ...`.

---

### Cumulative spend

```python
df["Cumulative_Spend"] = df.apply(
    lambda r: r["Amount"] if r["Type"] == "Debit" else 0, axis=1
).cumsum()
```

- `axis=1` — apply row-by-row (axis=0 would be column-by-column)
- `.cumsum()` — cumulative sum: `[100, 200, 50]` → `[100, 300, 350]`

This gives the running total of money spent across the month.

---

# Part VI — PDF Report Generation

---

## Chapter 17: Matplotlib — Creating Charts

**What you'll understand after this chapter:**
How matplotlib draws charts and how the chart style is configured.

---

### The basic pattern

```python
import matplotlib.pyplot as plt

fig, ax = plt.subplots()      # create figure and axes
ax.bar(["Food", "Transport"], [5200, 1800])  # draw a bar chart
ax.set_title("Spending")
fig.savefig("chart.png")
plt.close(fig)                # always close to free memory
```

`fig` is the whole canvas. `ax` is one chart area on the canvas. A figure can have multiple axes (subplots).

---

### The `Agg` backend

```python
import matplotlib
matplotlib.use("Agg")   # must be called before importing pyplot
import matplotlib.pyplot as plt
```

Matplotlib has different "backends" for rendering. The default tries to open a GUI window. On a server (EC2, Docker) there is no GUI. `"Agg"` renders to memory only — no window, just files.

---

### Custom style

```python
C = {
    "bg":      "#FAFAFA",
    "primary": "#2563EB",
    "text":    "#1E293B",
    "muted":   "#64748B",
    "border":  "#E2E8F0",
}

def _style():
    plt.rcParams.update({
        "figure.facecolor": C["bg"],
        "axes.facecolor":   C["card"],
        "axes.titlesize":   11,
        "axes.spines.top":  False,    # remove top border line
        "axes.spines.right":False,    # remove right border line
        "font.family":      "DejaVu Sans",
    })
```

`plt.rcParams` is a global dictionary of matplotlib settings. Updating it once before drawing any charts makes all charts consistent.

---

### Subplots — multiple charts on one page

```python
import matplotlib.gridspec as gridspec

fig = plt.figure(figsize=(11.69, 8.27))  # A4 landscape in inches
gs  = gridspec.GridSpec(2, 3, figure=fig)  # 2 rows, 3 columns

ax1 = fig.add_subplot(gs[0, 0])   # top-left
ax2 = fig.add_subplot(gs[0, 1])   # top-middle
ax3 = fig.add_subplot(gs[0, :])   # top row, spans all 3 columns
ax4 = fig.add_subplot(gs[1, 0:2]) # bottom, spans first 2 columns
```

`GridSpec` gives precise control over layout — far more flexible than `plt.subplots(2, 3)`.

---

### Common chart types used in the report

```python
# Bar chart
ax.bar(labels, values, color=C["primary"])

# Horizontal bar chart
ax.barh(labels, values, color=colors)

# Line chart with markers
ax.plot(dates, amounts, color=C["primary"], linewidth=2, marker="o", markersize=4)

# Donut chart (pie with a hole)
ax.pie(sizes, labels=labels, colors=CAT_COLORS, startangle=90,
       wedgeprops={"width": 0.5})   # width < 1 creates the hole

# Heatmap (using imshow)
ax.imshow(matrix, cmap="Blues", aspect="auto")
```

---

## Chapter 18: Multi-Page PDF Reports

**What you'll understand after this chapter:**
How multiple matplotlib figures are combined into a single PDF file.

---

### `PdfPages` — the multi-page PDF writer

```python
from matplotlib.backends.backend_pdf import PdfPages

def generate(csv_path, output_pdf):
    with PdfPages(output_pdf) as pdf:
        # Page 1: Summary
        fig1 = _draw_summary_page(df)
        pdf.savefig(fig1)
        plt.close(fig1)

        # Page 2: Trends
        fig2 = _draw_trends_page(df)
        pdf.savefig(fig2)
        plt.close(fig2)

        # Page 3: Categories
        fig3 = _draw_categories_page(df)
        pdf.savefig(fig3)
        plt.close(fig3)
```

`pdf.savefig(fig)` appends a matplotlib figure as a new page. The `with` block closes and writes the PDF when done.

---

### The `generate()` function flow

```
generate(csv_path, output_pdf)
  ↓
pd.read_csv(csv_path)          → load the enriched data
  ↓
_style()                       → apply matplotlib theme
  ↓
For each page section:
  create fig with gridspec
  draw charts on axes
  add text annotations
  pdf.savefig(fig)
  plt.close(fig)
  ↓
PdfPages writes the file
```

---

### Stat boxes — the summary cards

```python
def _stat_box(ax, label, value, color=None):
    ax.axis("off")                              # no axes lines or ticks
    ax.set_facecolor(color or C["primary"])     # colored background
    ax.text(0.5, 0.62, value,
            ha="center", va="center",
            transform=ax.transAxes,             # use 0-1 coordinate system
            fontsize=14, fontweight="bold", color="white")
    ax.text(0.5, 0.25, label,
            ha="center", va="center",
            transform=ax.transAxes,
            fontsize=8, color="white")
```

`ax.axis("off")` hides all axes lines and ticks — the axes object becomes a blank canvas for text and shapes.

`transform=ax.transAxes` — coordinates `(0.5, 0.5)` mean the center of the axes box, regardless of data scale. Much easier for placing text labels.

---

# Part VII — Production

---

## Chapter 19: Docker — Containerizing the App

**What you'll understand after this chapter:**
Every line of the Dockerfile and why it's structured the way it is.

---

### The full Dockerfile

```dockerfile
FROM python:3.12-slim

COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    libgl1 \
    libglib2.0-0 \
    fontconfig \
    && rm -rf /var/lib/apt/lists/*

COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev

COPY app.py spending_pipeline.py generate_report.py data_loader.py ./

ENV FILES_DIR=/tmp/spending-files

EXPOSE 8000

CMD ["/app/.venv/bin/gunicorn", "app:app", \
     "-w", "2", \
     "-k", "uvicorn.workers.UvicornWorker", \
     "--bind", "0.0.0.0:8000", \
     "--timeout", "1200"]
```

---

### Line by line

**`FROM python:3.12-slim`**

The base image. `slim` is a minimal Python 3.12 Linux image — no unnecessary packages, small size.

**`COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv`**

Copies the `uv` binary from the official uv Docker image into our image. The easiest way to install uv in Docker.

**`WORKDIR /app`**

All subsequent commands run from `/app`. File paths without `/` are relative to this.

**`RUN apt-get install -y libgl1 libglib2.0-0 fontconfig`**

System libraries required by:
- `libgl1` — OpenGL library that PyMuPDF depends on
- `libglib2.0-0` — GLib, another PyMuPDF dependency
- `fontconfig` — font management, needed by matplotlib to render text in charts

`--no-install-recommends` — install only what's listed, no suggested packages (keeps image small).
`rm -rf /var/lib/apt/lists/*` — delete the apt package cache (smaller image).

**`COPY pyproject.toml uv.lock ./`** then **`RUN uv sync --frozen --no-dev`**

Installing dependencies **before** copying application code. This is critical for **Docker layer caching**:

```
Layer 1: base python image
Layer 2: uv binary
Layer 3: system libraries (apt-get)
Layer 4: pyproject.toml + uv.lock     ← only rebuilds if dependencies change
Layer 5: uv sync (install packages)   ← only rebuilds if dependencies change
Layer 6: application code             ← rebuilds every time code changes
```

If only `app.py` changes, Docker reuses layers 1–5 from cache. Only layer 6 rebuilds. Without this ordering, every code change would reinstall all 14 packages from scratch.

**`COPY app.py spending_pipeline.py generate_report.py data_loader.py ./`**

Copy only the application files — not tests, not development configs.

**`ENV FILES_DIR=/tmp/spending-files`**

Set a default environment variable inside the container.

**`EXPOSE 8000`**

Documents that the container listens on port 8000. (This alone doesn't open the port — you still need `-p 8000:8000` when running.)

**`CMD [...]`**

The default command that runs when the container starts:
```
gunicorn app:app        ← file app.py, object named app
-w 2                    ← 2 worker processes
-k uvicorn.workers.UvicornWorker  ← use uvicorn as the ASGI worker
--bind 0.0.0.0:8000    ← listen on all interfaces at port 8000
--timeout 1200          ← 20-minute timeout per request
```

---

### Building and running

```bash
# Build the image
docker build -t souravm47/portfolio .

# Run it
docker run -d \
  -p 8000:8000 \
  -e API_KEY=gsk_your_key \
  -e BASE_URL=https://api.groq.com/openai/v1 \
  -e MODEL=meta-llama/llama-4-scout-17b-16e-instruct \
  --restart unless-stopped \
  souravm47/portfolio
```

---

## Chapter 20: Nginx — The Gatekeeper

**What you'll understand after this chapter:**
What Nginx does in this deployment and why it sits in front of FastAPI.

---

### Why Nginx at all?

FastAPI/Uvicorn could listen on port 80 directly. But Nginx provides:
1. **SSL termination** — handles HTTPS encryption, forwards plain HTTP to FastAPI
2. **Static file serving** — serves the React build files directly (faster than Python)
3. **Rate limiting** — limits requests per IP to prevent abuse
4. **Request size limit** — second line of defence against huge uploads
5. **Long timeouts** — the AI pipeline takes 60–120s; Nginx needs to be patient

---

### The architecture

```
Internet → Nginx (port 80/443)
                │
                ├── /assets/* , /*.js → serve from /var/www/portfolio/frontend/dist
                ├── /gallery/*        → serve from /var/www/portfolio/frontend/dist
                │
                └── /analyse , /health , /files/* → proxy to FastAPI (127.0.0.1:8000)
```

Nginx handles everything. FastAPI never talks to the internet directly.

---

### The two-server-block structure

`nginx.conf` contains two `server {}` blocks:

**Block 1 — HTTP → HTTPS redirect:**

```nginx
server {
    listen 80;
    listen [::]:80;
    server_name YOUR_DOMAIN www.YOUR_DOMAIN;
    return 301 https://$host$request_uri;
}
```

Any plain HTTP request (`http://`) gets a permanent redirect (301) to the HTTPS version. This ensures all traffic is encrypted.

**Block 2 — HTTPS main server:**

```nginx
server {
    listen 443 ssl http2;
    ssl_certificate     /etc/letsencrypt/live/YOUR_DOMAIN/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/YOUR_DOMAIN/privkey.pem;
    include             /etc/letsencrypt/options-ssl-nginx.conf;
    ssl_dhparam         /etc/letsencrypt/ssl-dhparams.pem;
    ...
}
```

The SSL cert paths are populated by Certbot: `sudo certbot --nginx -d YOUR_DOMAIN`. Certbot writes the cert files and updates these paths automatically.

---

### Security headers

These headers are added inside the HTTPS server block:

```nginx
add_header Strict-Transport-Security "max-age=63072000; includeSubDomains; preload" always;
add_header X-Frame-Options           "DENY"                             always;
add_header X-Content-Type-Options    "nosniff"                          always;
add_header Referrer-Policy           "strict-origin-when-cross-origin"  always;
add_header Content-Security-Policy   "default-src 'self'; ..." always;
```

What each one does:

| Header | What it prevents |
|--------|----------------|
| **HSTS** (`Strict-Transport-Security`) | Browser always uses HTTPS for 2 years — cannot be downgraded to HTTP even if the user types `http://` |
| **X-Frame-Options: DENY** | Clickjacking — prevents the site from being embedded in an iframe on another domain |
| **X-Content-Type-Options: nosniff** | MIME sniffing attacks — browser must use the declared `Content-Type`, not guess |
| **Referrer-Policy** | Prevents the full URL (including query params) from leaking to third-party servers when navigating away |
| **Content-Security-Policy** | Controls which resources the browser can load. `'unsafe-inline'` is required for Vite's build; `frame-ancestors 'none'` duplicates X-Frame-Options for modern browsers |

The `always` keyword ensures headers are sent even on error responses (4xx, 5xx), not only on 200 OK.

---

### Forwarding the consent header

```nginx
location /api/ {
    ...
    proxy_pass_header X-Consent-Given;
    ...
}
```

By default nginx strips most custom request headers before forwarding to the backend. `proxy_pass_header X-Consent-Given` tells nginx to forward this specific header through to FastAPI. Without this line, the consent check in `app.py` would always fail — it would never see the header the browser sent.

---

### Key nginx.conf sections

**Rate limiting:**

```nginx
limit_req_zone $binary_remote_addr zone=api:10m rate=2r/s;
```

Max 2 requests per second per IP address. `zone=api:10m` — store IP data in 10MB of shared memory. This must be defined in the `http {}` block of `/etc/nginx/nginx.conf` (the global config), not inside the site config.

**Serving static React files:**

```nginx
location / {
    root /var/www/spending-portfolio;
    try_files $uri $uri/ /index.html;
}
```

`try_files $uri $uri/ /index.html` — try the exact path, then a directory, then fall back to `index.html`. This is what makes React client-side routing work (all routes return `index.html`, React handles navigation internally).

**Proxying to FastAPI:**

```nginx
location /api/ {
    proxy_pass http://127.0.0.1:8000/;
    proxy_read_timeout    300s;
    proxy_send_timeout    300s;
    client_max_body_size  16m;
}
```

`proxy_pass` forwards matching requests to FastAPI. The trailing `/` in `http://127.0.0.1:8000/` strips the `/api` prefix before forwarding — so `/api/analyse` becomes `/analyse` on the backend. `proxy_read_timeout 300s` — wait up to 5 minutes for a response (the AI pipeline can be slow).

---

## Chapter 21: Testing with pytest

**What you'll understand after this chapter:**
How the integration tests work and how to run them.

---

### What is an integration test?

A **unit test** tests one function in isolation.
An **integration test** tests the whole system end-to-end — it actually calls the Groq API, runs the pipeline, checks the output.

`test_integration.py` runs the full pipeline once with a real PDF (if available) and verifies the output at multiple levels.

---

### pytest basics

```python
import pytest

def test_something():
    result = add(2, 3)
    assert result == 5   # test passes if True, fails if False

def test_raises_error():
    with pytest.raises(ValueError):
        int("not a number")   # test passes if ValueError is raised
```

Any function starting with `test_` is automatically discovered and run by pytest.

---

### Fixtures — shared setup

```python
@pytest.fixture(scope="session")
def pipeline_result(tmp_path_factory):
    """Run the pipeline once; all tests in this session share the result."""
    tmp = tmp_path_factory.mktemp("data")
    # ... copy test PDFs to tmp, run pipeline ...
    return df   # shared across all test functions that request this fixture
```

`scope="session"` — the fixture runs once for the entire test run, not once per test. This prevents calling the Groq API 29 times (once per test) — it runs once, and all tests share the result.

---

### Testing the HTTP API

```python
from fastapi.testclient import TestClient
from app import app

client = TestClient(app)

def test_health():
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json() == {"status": "ok"}

def test_invalid_extension():
    r = client.post("/analyse", files={"files": ("x.txt", b"content", "text/plain")})
    assert r.status_code == 400
```

`TestClient` from FastAPI wraps the app and lets you make HTTP requests in tests without actually running a server.

---

### Running the tests

```bash
cd backend/budget-tracker

# Run all tests
uv run pytest test_integration.py -v

# Run only API tests
uv run pytest test_integration.py::TestAPI -v

# Run one specific test
uv run pytest test_integration.py::TestAPI::test_health -v
```

---

# Appendix

---

## Glossary

| Term | Plain English meaning |
|------|-----------------------|
| **API** | A contract between programs. Defines URLs, expected inputs, and outputs. |
| **HTTP** | The protocol browsers and servers use to communicate. Request → Response. |
| **GET / POST** | HTTP methods. GET = fetch. POST = submit. |
| **Status code** | A 3-digit number in every HTTP response. 200 = OK, 400 = bad request, 500 = server error. |
| **JSON** | A text format for structured data: `{"key": "value", "list": [1, 2, 3]}`. |
| **FastAPI** | Python web framework. Turns decorated functions into HTTP endpoints. |
| **Route** | A function that handles a specific URL + method. `@app.get("/health")`. |
| **Uvicorn** | ASGI server that runs FastAPI. Handles one process. |
| **Gunicorn** | Process manager that runs multiple Uvicorn workers. |
| **CORS** | Browser security policy. Servers must explicitly allow cross-origin requests. |
| **Middleware** | Code that runs on every request/response, regardless of route. |
| **async / await** | Python syntax for non-blocking I/O. Pauses a function while waiting. |
| **Multipart form data** | HTTP encoding for file uploads. Used by browser `<form>` and `FormData`. |
| **UUID** | A universally unique identifier. 36-character string. Used for job IDs. |
| **Environment variable** | A key-value setting outside the code. Loaded with `os.environ.get()`. |
| **`.env` file** | A local file holding environment variables for development. Never committed. |
| **`python-dotenv`** | Library that reads `.env` files into `os.environ`. |
| **Pandas** | Python library for tabular data. `DataFrame` = in-memory spreadsheet. |
| **DataFrame** | A 2D table in pandas. Has rows and columns. |
| **`apply()`** | Pandas method to run a function on each row or cell of a column. |
| **`groupby()`** | Pandas method to aggregate rows by a shared value. |
| **PyMuPDF (`fitz`)** | Python library for reading, rendering, and extracting from PDF files. |
| **Base64** | Encoding scheme that converts binary data (images, files) to text. |
| **Data URL** | A URL that embeds file content directly as base64. `data:image/png;base64,...` |
| **Vision AI** | An AI model that can interpret images. Reads PDFs as pictures. |
| **Rate limiting** | Restricting how many API calls you can make in a time window. |
| **Exponential backoff** | Retry strategy: wait 2s, then 4s, then 8s... avoids hammering a rate-limited API. |
| **Regex** | Regular expression — a pattern language for searching text. `re.search()`. |
| **Matplotlib** | Python chart library. Draws bar charts, line charts, pie charts, heatmaps, etc. |
| **`Agg` backend** | Matplotlib rendering mode that works on servers (no GUI required). |
| **`PdfPages`** | Matplotlib utility that combines multiple figures into one PDF file. |
| **Docker** | Packages an app and its environment into a portable container image. |
| **Container** | A running Docker image. Isolated from the host system. |
| **Dockerfile** | Build instructions for a Docker image. |
| **Layer caching** | Docker reuses unchanged build steps. Copy dependencies before code for fast rebuilds. |
| **Nginx** | High-performance web server and reverse proxy. |
| **Reverse proxy** | A server that forwards requests to a backend. Clients talk to Nginx, Nginx talks to FastAPI. |
| **SSL termination** | Nginx handles HTTPS encryption/decryption. FastAPI gets plain HTTP. |
| **Rate limiting (Nginx)** | `limit_req_zone` — caps requests per IP to prevent abuse. |
| **`try_files`** | Nginx directive. Tries multiple paths; falls back to `index.html` for React routing. |
| **pytest** | Python testing framework. Runs any function starting with `test_`. |
| **Fixture** | Shared setup code in pytest. `scope="session"` runs it once for all tests. |
| **`TestClient`** | FastAPI's in-process HTTP client for writing API tests without a running server. |
| **Integration test** | A test that runs the full system end-to-end, not a single function in isolation. |
| **`uv`** | A fast Python package manager. Replaces `pip`. `uv sync --frozen` = reproducible installs. |
| **`pyproject.toml`** | Python project config file. Lists dependencies, Python version, project metadata. |
| **`uv.lock`** | Locked dependency versions. Ensures everyone runs the same exact library versions. |
| **Strategy pattern** | A design pattern where a behaviour (e.g., loading data) is swappable. `data_loader.py`. |
| **`shutil.rmtree`** | Recursively deletes a folder and all its contents. |
| **`daemon=True`** | A background thread that automatically exits when the main program exits. |
| **Path traversal** | A security attack using `../` in filenames to escape the intended directory. |

---

*Last updated: May 2026*
*Covers: app.py, spending_pipeline.py, report/ package (orchestrator, scorer, recommender, theme, 10 page modules), data_loader.py, Dockerfile, nginx.conf, test_report.py, test_integration.py*
*When a new module is added — add its chapter under Part V or VI and update this date.*
