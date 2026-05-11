#!/usr/bin/env python3
"""
===============================================================================
PERSONAL SPENDING PIPELINE  —  Vision Edition
===============================================================================
Parses ANY bank / credit card / UPI PDF statement + manual offline spreadsheet.

Engine: PyMuPDF renders each PDF page as a high-resolution image → Llama 4
Scout (via Groq free API) reads it like a human, independent of PDF layout.

USAGE:
    python spending_pipeline.py /path/to/folder

FOLDER STRUCTURE:
    local-database/budget-tracker/monthly-data/
    ├── hdfc_credit_card.pdf          <- any bank statement PDF
    ├── gpay_march.pdf                <- any UPI summary PDF
    └── offline_transactions.xlsx     <- manual cash entries (optional)

SETUP:
    pip install pymupdf openai pandas openpyxl python-dotenv
    .env file: MODEL=... BASE_URL=https://api.groq.com/openai/v1 API_KEY=gsk_...

Output: spending_YYYYMM.csv (Power BI-ready, 31 analytical columns)
===============================================================================
"""

import os
import re
import sys
import json
import base64
import time
import warnings
from datetime import datetime, timedelta

import pandas as pd
import fitz  # PyMuPDF
from dotenv import load_dotenv

load_dotenv()
warnings.filterwarnings("ignore")

# ============================================================
# CATEGORY MAPPING
# ============================================================
CATEGORY_RULES = [
    ("SWIGGY FOOD",        "Food & Dining",     "Swiggy Food"),
    ("SWIGGY INSTAMART",   "Groceries",         "Swiggy Instamart"),
    ("SWIGGY",             "Food & Dining",     "Swiggy"),
    ("ZOMATO",             "Food & Dining",     "Zomato"),
    ("BLINKIT",            "Groceries",         "Blinkit"),
    ("ZEPTO",              "Groceries",         "Zepto"),
    ("ZEPTONOW",           "Groceries",         "Zepto"),
    ("BIGBASKET",          "Groceries",         "BigBasket"),
    ("GROFERS",            "Groceries",         "Blinkit"),
    ("SAWARRAM",           "Groceries",         "Local Store"),
    ("MORE SANDIP",        "Groceries",         "Local Store"),
    ("MANGATRAM",          "Groceries",         "Local Store"),
    ("RAPIDO",             "Transport",         "Rapido"),
    ("UBER",               "Transport",         "Uber"),
    ("OLA",                "Transport",         "Ola"),
    ("RAILWAYS UTS",       "Transport",         "Local Train"),
    ("RAILWAYS TICKETING", "Transport",         "Train Ticket"),
    ("INDIAN RAILWAYS",    "Transport",         "Train Ticket"),
    ("METRO OPERATION",    "Transport",         "Metro"),
    ("MMRDA",              "Transport",         "Metro/Monorail"),
    ("FLAT OWNER",         "Housing",           "Rent"),
    ("RENT",               "Housing",           "Rent"),
    ("SOCIETY",            "Housing",           "Maintenance"),
    ("MSEDCL",             "Utilities",         "Electricity"),
    ("MAHAVITARAN",        "Utilities",         "Electricity"),
    ("CESC",               "Utilities",         "Electricity"),
    ("BESCOM",             "Utilities",         "Electricity"),
    ("TATA POWER",         "Utilities",         "Electricity"),
    ("JIO PREPAID",        "Utilities",         "Mobile Recharge"),
    ("JIO POSTPAID",       "Utilities",         "Mobile Recharge"),
    ("AIRTEL",             "Utilities",         "Mobile Recharge"),
    ("BSNL",               "Utilities",         "Mobile Recharge"),
    ("VI PREPAID",         "Utilities",         "Mobile Recharge"),
    ("CLAUDE",             "Subscriptions",     "Claude AI"),
    ("CHATGPT",            "Subscriptions",     "ChatGPT"),
    ("OPENAI",             "Subscriptions",     "ChatGPT"),
    ("NETFLIX",            "Subscriptions",     "Netflix"),
    ("HOTSTAR",            "Subscriptions",     "Hotstar"),
    ("PRIME VIDEO",        "Subscriptions",     "Prime Video"),
    ("HOICHOI",            "Subscriptions",     "Hoichoi"),
    ("YOUTUBE PREMIUM",    "Subscriptions",     "YouTube Premium"),
    ("SPOTIFY",            "Subscriptions",     "Spotify"),
    ("GAANA",              "Subscriptions",     "Gaana"),
    ("APPLE MEDIA",        "Subscriptions",     "Apple Services"),
    ("APPLE SERVICE",      "Subscriptions",     "Apple Services"),
    ("GOOGLE PLAY",        "Subscriptions",     "Google Play"),
    ("ADOBE",              "Subscriptions",     "Adobe"),
    ("NOTION",             "Subscriptions",     "Software"),
    ("FIGMA",              "Subscriptions",     "Software"),
    ("GITHUB",             "Subscriptions",     "Software"),
    ("AMAZON",             "Shopping",          "Amazon"),
    ("FLIPKART",           "Shopping",          "Flipkart"),
    ("MYNTRA",             "Shopping",          "Myntra"),
    ("AJIO",               "Shopping",          "Ajio"),
    ("MEESHO",             "Shopping",          "Meesho"),
    ("NYKAA",              "Shopping",          "Nykaa"),
    ("MAKE MY TRIP",       "Travel",            "MakeMyTrip"),
    ("MAKEMYTRIP",         "Travel",            "MakeMyTrip"),
    ("CONFIRMTKT",         "Travel",            "ConfirmTkt"),
    ("IXIGO",              "Travel",            "Ixigo"),
    ("CLEARTRIP",          "Travel",            "ClearTrip"),
    ("GOIBIBO",            "Travel",            "Goibibo"),
    ("IRCTC",              "Travel",            "IRCTC"),
    ("ECO TOURISM",        "Travel",            "Tourism"),
    ("MAHAECO",            "Travel",            "Tourism"),
    ("CAFE",               "Food & Dining",     "Cafe"),
    ("CAFFE",              "Food & Dining",     "Cafe"),
    ("RESTAURANT",         "Food & Dining",     "Restaurant"),
    ("SNACKS",             "Food & Dining",     "Snacks/Sweets"),
    ("SWEETS",             "Food & Dining",     "Snacks/Sweets"),
    ("TEA STALL",          "Food & Dining",     "Tea/Chai"),
    ("VEG WORLD",          "Food & Dining",     "Restaurant"),
    ("SNABBIT",            "Services",          "Home Services (Snabbit)"),
    ("URBAN COMPANY",      "Services",          "Home Services"),
    ("URBAN CLAP",         "Services",          "Home Services"),
    ("RENTOMOJO",          "Services",          "Furniture Rental"),
    ("FURLENCO",           "Services",          "Furniture Rental"),
    ("SALOON",             "Personal Care",     "Grooming"),
    ("SALON",              "Personal Care",     "Grooming"),
    ("PARLOUR",            "Personal Care",     "Grooming"),
    ("STUDIO",             "Personal Care",     "Photography/Studio"),
    ("EMI,PRIN",           "EMI Payments",      "EMI Principal"),
    ("EMI ,PRIN",          "EMI Payments",      "EMI Principal"),
    ("EMI,INT",            "EMI Payments",      "EMI Interest"),
    ("EMI ,INT",           "EMI Payments",      "EMI Interest"),
    ("MER EMI",            "EMI Payments",      "Merchant EMI"),
    ("SMARTEMI",           "EMI Payments",      "SmartEMI"),
    ("PROCNG FEE",         "Fees & Charges",    "Processing Fee"),
    ("PROCESSING FEE",     "Fees & Charges",    "Processing Fee"),
    ("FCY MARKUP",         "Fees & Charges",    "Forex Markup"),
    ("IGST",               "Fees & Charges",    "GST/Tax"),
    ("LATE PAYMENT",       "Fees & Charges",    "Late Fee"),
    ("ANNUAL FEE",         "Fees & Charges",    "Annual Fee"),
    ("CASHBACK",           "Cashback/Rewards",  "Cashback"),
    ("REWARD",             "Cashback/Rewards",  "Reward Points"),
    ("CREDIT CARD PAYMENT","Transfers",         "CC Payment"),
    ("NEFT",               "Transfers",         "Bank Transfer"),
    ("IMPS",               "Transfers",         "Bank Transfer"),
]


def categorize_transaction(description):
    desc_upper = description.upper()
    for keyword, category, subcategory in CATEGORY_RULES:
        if keyword.upper() in desc_upper:
            return category, subcategory
    return "Uncategorized", "Other"


# ============================================================
# SOURCE DETECTION
# ============================================================

def detect_pdf_source(pdf_path):
    """Peek at first page text to identify bank/app and payment mode."""
    try:
        doc  = fitz.open(pdf_path)
        text = doc[0].get_text().upper()
        doc.close()
    except Exception:
        text = ""

    if "GOOGLE PAY" in text and "TRANSACTION STATEMENT" in text:
        return "Google Pay", "UPI"
    if "HDFC" in text and "CREDIT CARD" in text:
        return "HDFC Credit Card", "Credit Card"
    if "HDFC" in text:
        return "HDFC Bank", "Debit Card"
    if "STATE BANK" in text or "SBI CARD" in text:
        return "SBI", "Credit Card"
    if "ICICI" in text:
        return "ICICI Bank", "Credit Card"
    if "AXIS" in text:
        return "Axis Bank", "Credit Card"
    if "KOTAK" in text:
        return "Kotak Bank", "Credit Card"
    if "PAYTM" in text:
        return "Paytm", "UPI"
    if "PHONEPE" in text:
        return "PhonePe", "UPI"
    if "AMAZON PAY" in text:
        return "Amazon Pay", "UPI"
    name = os.path.splitext(os.path.basename(pdf_path))[0]
    return name, "Unknown"


# ============================================================
# VISION PROMPT
# ============================================================

VISION_PROMPT = """You are a financial transaction extractor reading a bank statement page image.

TASK: Extract every individual transaction row visible on this page.

Return ONLY valid JSON — no markdown, no explanation:
{"transactions":[{"date":"DD/MM/YYYY","time":"HH:MM or empty","description":"merchant or payee name","amount":123.45,"type":"Debit or Credit"}]}

=== CLASSIFICATION RULES ===

CREDIT CARD statements (HDFC, SBI Card, ICICI, Axis, Kotak, etc.):
- Purchase / Fee / Interest / EMI charge  → type = "Debit"   (money you owe the bank)
- Cashback / Reward point credit          → type = "Credit"  (bank gives you money back)
- Your payment to the card (NEFT/IMPS)   → type = "Transfer"
- DO NOT include: Opening Balance row, Closing Balance row, Total Amount Due row,
  Minimum Payment Due row, Credit Limit row. These are summaries, NOT transactions.

UPI / Payment app statements (Google Pay, PhonePe, Paytm, Amazon Pay):
- Money you SENT to someone               → type = "Debit"
- Money you RECEIVED from someone         → type = "Credit"
- DO NOT include: Account balance rows, running balance column values.

BANK ACCOUNT statements (savings/current account):
- Withdrawals / Debits / Dr entries       → type = "Debit"
- Deposits / Credits / Cr entries         → type = "Credit"
- DO NOT include: Opening/Closing balance rows.

=== AMOUNT RULES ===
- amount must be a positive number (e.g. 250.00 not -250)
- amount must be the actual transaction value — NOT a running balance
- If a row has no clear transaction amount, skip it
- If no transactions appear on this page, return {"transactions":[]}

=== DESCRIPTION RULES ===
- Use the merchant/payee name or a short clear label
- Strip reference numbers, UTR IDs, account numbers
- Keep it human-readable (e.g. "Swiggy", "Rapido", "MSEDCL Electricity")
"""


# ============================================================
# VLM CLIENT  — reads config from .env
# ============================================================

def _parse_retry_after(err_str):
    """Extract sleep seconds from Groq 'try again in Xm Y.Zs' message."""
    m = re.search(r'try again in (?:(\d+)m)?(\d+(?:\.\d+)?)s', err_str)
    if m:
        minutes = int(m.group(1)) if m.group(1) else 0
        return int(float(m.group(2)) + minutes * 60) + 5  # 5 s buffer
    return None


def _make_client():
    api_key  = os.environ.get("API_KEY")
    base_url = os.environ.get("BASE_URL", "").strip()
    if not api_key:
        raise RuntimeError("No API key found. Set API_KEY in .env")
    from openai import OpenAI
    return OpenAI(api_key=api_key, base_url=base_url or None)


def _model_name():
    return os.environ.get("MODEL", "llama-3.2-11b-vision-preview").strip()


def _call_vision(client, model, img_b64, system_prompt, user_text):
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user",   "content": [
            {"type": "text",      "text": user_text},
            {"type": "image_url", "image_url": {
                "url":    f"data:image/png;base64,{img_b64}",
                "detail": "high",
            }},
        ]},
    ]
    resp = client.chat.completions.create(
        model=model, temperature=0,
        response_format={"type": "json_object"},
        messages=messages,
    )
    return resp.choices[0].message.content


# ============================================================
# VISION PARSER
# ============================================================

def parse_pdf_vision(pdf_path):
    """
    Render each PDF page as a high-resolution image and send to a
    configurable VLM (Ollama / Groq / OpenAI) to extract transactions.
    Works on any bank/UPI/CC PDF regardless of layout.
    """
    try:
        client = _make_client()
    except RuntimeError as e:
        print(f"  [ERROR] {e}")
        return []

    model = _model_name()
    source, payment_mode = detect_pdf_source(pdf_path)
    is_cc = payment_mode == "Credit Card"

    try:
        doc = fitz.open(pdf_path)
    except Exception as e:
        print(f"  [ERROR] Cannot open {os.path.basename(pdf_path)}: {e}")
        return []

    n_pages = len(doc)
    backend = os.environ.get("BASE_URL", "groq.com").split("//")[-1].split("/")[0]
    print(f"  [PDF] {os.path.basename(pdf_path)} -> {source} ({n_pages} pages) [{model} @ {backend}]")

    transactions = []

    for page_num in range(n_pages):
        # Pace calls to stay under Groq free-tier TPM limit before every page
        if page_num > 0:
            time.sleep(25)

        page = doc.load_page(page_num)

        zoom = 1.0
        mat = fitz.Matrix(zoom, zoom)
        pix = page.get_pixmap(matrix=mat, alpha=False)
        img_b64 = base64.b64encode(pix.tobytes("png")).decode()

        context = (
            f"This is page {page_num + 1} of {n_pages} from a "
            f"{'credit card' if is_cc else 'bank/UPI'} statement "
            f"({source}). Extract all transactions."
        )

        raw = None
        page_rate_limited = False
        for attempt in range(6):
            try:
                raw = _call_vision(client, model, img_b64, VISION_PROMPT, context)
                break
            except Exception as e:
                err = str(e)
                if "429" in err or "rate_limit" in err.lower():
                    wait = _parse_retry_after(err) or min(2 ** (attempt + 1), 60)
                    print(f"       Page {page_num + 1}: rate limit, retrying in {wait}s...")
                    time.sleep(wait)
                    page_rate_limited = True
                else:
                    print(f"       Page {page_num + 1}: error — {e}")
                    break
        if raw is None:
            print(f"       Page {page_num + 1}: skipped after all retries exhausted")
            continue

        try:
            page_txns = json.loads(raw).get("transactions", [])
        except json.JSONDecodeError:
            continue

        for txn in page_txns:
            if not all(k in txn for k in ("date", "description", "amount", "type")):
                continue

            # ── amount ──────────────────────────────────────────────────────
            try:
                amount = float(
                    str(txn["amount"])
                    .replace(",", "")
                    .replace("Rs.", "")
                    .replace("INR", "")
                    .strip()
                )
            except (ValueError, TypeError):
                continue
            if amount <= 0:
                continue

            # ── date ─────────────────────────────────────────────────────────
            date_str = str(txn["date"]).strip()
            txn_date = None
            for fmt in (
                "%d/%m/%Y", "%d-%m-%Y", "%d %b %Y", "%d %B %Y",
                "%Y-%m-%d", "%m/%d/%Y", "%d %b, %Y",
                "%d/%m/%y", "%d-%m-%y",
            ):
                try:
                    txn_date = datetime.strptime(date_str, fmt)
                    break
                except ValueError:
                    continue
            if not txn_date:
                continue

            # ── description ──────────────────────────────────────────────────
            description = str(txn["description"]).strip()
            if not description or len(description) < 2:
                continue

            # Skip obvious balance / summary rows that slip through
            desc_up = description.upper()
            skip_keywords = (
                "OPENING BALANCE", "CLOSING BALANCE", "TOTAL AMOUNT DUE",
                "MINIMUM AMOUNT DUE", "MINIMUM DUE", "CREDIT LIMIT",
                "AVAILABLE CREDIT", "TOTAL OUTSTANDING", "STATEMENT BALANCE",
                "ACCOUNT BALANCE", "RUNNING BALANCE",
            )
            if any(kw in desc_up for kw in skip_keywords):
                continue

            # Skip DIAL AN/EN EMI — these are EMI conversion notices that
            # duplicate the original purchase (same amount listed twice)
            if re.search(r"DIAL\s+(AN|EN)\s+EMI", desc_up):
                continue

            # ── type ─────────────────────────────────────────────────────────
            raw_type = str(txn.get("type", "")).strip().lower()
            if raw_type == "credit":
                txn_type = "Credit"
            elif raw_type == "transfer":
                txn_type = "Transfer"
            else:
                txn_type = "Debit"

            # Auto-fix common mis-classifications
            if any(w in desc_up for w in ("CASHBACK", "REFUND", "REWARD", "REVERSAL")):
                txn_type = "Credit"
            elif any(w in desc_up for w in ("NEFT", "IMPS", "RTGS")) and is_cc:
                txn_type = "Transfer"  # card payment
            elif "SELF TRANSFER" in desc_up:
                txn_type = "Transfer"  # GPay self-transfers to own bank account
            elif (payment_mode == "UPI"
                  and re.match(r"^(STATE BANK|SBI|HDFC|ICICI|AXIS|KOTAK|BOB|PNB|CANARA)"
                               r".*\d{4,}", desc_up)):
                # Bare "Bank Name XXXX" in a UPI statement with no person's name
                # is almost always a self-transfer to own savings account
                txn_type = "Transfer"

            category, subcategory = categorize_transaction(description)

            # Adjust category for Credits/Transfers
            if txn_type == "Credit":
                if any(w in desc_up for w in ("CASHBACK", "REWARD")):
                    category, subcategory = "Cashback/Rewards", "Cashback"
                elif "RECEIVED" in desc_up:
                    category, subcategory = "Income/Received", "P2P Received"
            elif txn_type == "Transfer":
                if "SELF TRANSFER" in desc_up:
                    category, subcategory = "Transfers", "Self Transfer"
                else:
                    category, subcategory = "Transfers", "CC Payment"

            time_str = str(txn.get("time", "")).strip()

            transactions.append({
                "Date":         txn_date,
                "Time":         time_str,
                "Description":  description,
                "Amount":       amount,
                "Type":         txn_type,
                "Source":       source,
                "Account":      source,
                "Payment_Mode": payment_mode,
                "Category":     category,
                "Subcategory":  subcategory,
                "UPI_ID":       "",
                "Bank":         source,
            })

    doc.close()

    # Correct implausible dates: if year is > 2 years off from the mode year,
    # the model likely misread a 2-digit year (e.g. EMI origination date).
    # We correct the year rather than drop the row.
    if transactions:
        years = [t["Date"].year for t in transactions]
        mode_year = max(set(years), key=years.count)
        corrected_count = 0
        fixed = []
        for t in transactions:
            if abs(t["Date"].year - mode_year) > 2:
                try:
                    t["Date"] = t["Date"].replace(year=mode_year)
                    corrected_count += 1
                except ValueError:
                    continue  # e.g. Feb 29 in non-leap year
            fixed.append(t)
        transactions = fixed
        if corrected_count:
            print(f"       (corrected year on {corrected_count} transactions)")

    # Deduplicate: same date + description + amount may appear on adjacent pages
    seen = set()
    unique = []
    for t in transactions:
        key = (
            t["Date"].strftime("%Y-%m-%d"),
            t["Description"][:40].upper(),
            round(t["Amount"], 2),
        )
        if key not in seen:
            seen.add(key)
            unique.append(t)

    dupes = len(transactions) - len(unique)
    print(f"       -> {len(unique)} transactions  "
          f"({dupes} duplicates removed)")
    return unique


# ============================================================
# OFFLINE / MANUAL TRANSACTIONS (xlsx / csv)
# ============================================================

def parse_offline(file_path):
    ext = os.path.splitext(file_path)[1].lower()
    if ext in (".xlsx", ".xls"):
        df = pd.read_excel(file_path)
    elif ext == ".csv":
        df = pd.read_csv(file_path)
    else:
        print(f"  [Offline] Unsupported format: {ext}")
        return []

    df.columns = [c.strip().lower().replace(" ", "_") for c in df.columns]

    date_col = next((c for c in df.columns if "date" in c), None)
    desc_col = next((c for c in df.columns if any(
        k in c for k in ["desc", "narration", "detail", "note", "merchant"])), None)
    amt_col  = next((c for c in df.columns if "amount" in c or "amt" in c), None)

    if not date_col:
        print("  [Offline] ERROR: No 'date' column found.")
        return []
    if not desc_col:
        print("  [Offline] ERROR: No 'description' column found.")
        return []
    if not amt_col:
        print("  [Offline] ERROR: No 'amount' column found.")
        return []

    cat_col    = next((c for c in df.columns if "category" in c and "sub" not in c), None)
    subcat_col = next((c for c in df.columns if "subcategory" in c or "sub_category" in c), None)
    type_col   = next((c for c in df.columns if c in ("type", "txn_type", "transaction_type")), None)

    transactions = []
    for _, row in df.iterrows():
        if pd.isna(row[date_col]) or pd.isna(row[amt_col]):
            continue
        try:
            txn_date = pd.to_datetime(row[date_col], dayfirst=True)
        except Exception:
            continue

        description = str(row[desc_col]).strip()
        try:
            amount = float(str(row[amt_col]).replace(",", "").replace("Rs.", "").strip())
        except ValueError:
            continue

        txn_type = (
            str(row[type_col]).strip()
            if type_col and pd.notna(row.get(type_col))
            else "Debit"
        )

        if cat_col and pd.notna(row.get(cat_col)):
            category    = str(row[cat_col]).strip()
            subcategory = (
                str(row[subcat_col]).strip()
                if subcat_col and pd.notna(row.get(subcat_col))
                else "Other"
            )
        else:
            category, subcategory = categorize_transaction(description)

        transactions.append({
            "Date":         txn_date,
            "Time":         "",
            "Description":  description,
            "Amount":       amount,
            "Type":         txn_type,
            "Source":       "Offline/Cash",
            "Account":      "Cash",
            "Payment_Mode": "Cash",
            "Category":     category,
            "Subcategory":  subcategory,
            "UPI_ID":       "",
            "Bank":         "",
        })

    print(f"  [Offline] {len(transactions)} transactions from {os.path.basename(file_path)}")
    return transactions


# ============================================================
# ENRICHMENT — Power BI analytical columns
# ============================================================

def enrich_dataframe(df):
    df["Date"] = pd.to_datetime(df["Date"])
    df = df.sort_values("Date").reset_index(drop=True)

    df["Day"]         = df["Date"].dt.day
    df["Day_Name"]    = df["Date"].dt.day_name()
    df["Day_of_Week"] = df["Date"].dt.dayofweek        # 0=Mon, 6=Sun
    df["Week_Number"] = df["Date"].dt.isocalendar().week.astype(int)
    df["Month"]       = df["Date"].dt.month
    df["Month_Name"]  = df["Date"].dt.strftime("%B")
    df["Year"]        = df["Date"].dt.year
    df["Quarter"]     = df["Date"].dt.quarter
    df["Year_Month"]  = df["Date"].dt.strftime("%Y-%m")
    df["Is_Weekend"]  = df["Date"].dt.dayofweek.isin([5, 6]).map({True: "Yes", False: "No"})

    df["Week_Start"] = df["Date"] - pd.to_timedelta(df["Date"].dt.dayofweek, unit="D")
    df["Week_Label"] = (
        df["Week_Start"].dt.strftime("%d %b") + " - " +
        (df["Week_Start"] + timedelta(days=6)).dt.strftime("%d %b")
    )
    df.drop(columns=["Week_Start"], inplace=True)

    def time_bucket(t):
        if not t:
            return "Unknown"
        try:
            t = t.strip()
            hour = (
                datetime.strptime(t, "%I:%M %p").hour
                if ("AM" in t.upper() or "PM" in t.upper())
                else int(t.split(":")[0])
            )
        except Exception:
            return "Unknown"
        if 5  <= hour < 12: return "Morning (5AM-12PM)"
        if 12 <= hour < 17: return "Afternoon (12-5PM)"
        if 17 <= hour < 21: return "Evening (5-9PM)"
        return "Night (9PM-5AM)"

    df["Time_Bucket"] = df["Time"].apply(time_bucket)
    df["Is_Debit"]    = (df["Type"] == "Debit").astype(int)
    df["Is_Credit"]   = (df["Type"] == "Credit").astype(int)
    df["Is_Transfer"] = (df["Type"] == "Transfer").astype(int)

    def amount_bucket(a):
        if a <=    50: return "Rs.0-50 (Micro)"
        if a <=   200: return "Rs.51-200 (Small)"
        if a <=   500: return "Rs.201-500 (Medium)"
        if a <=  1000: return "Rs.501-1000 (Large)"
        if a <=  5000: return "Rs.1001-5000 (Major)"
        return "Rs.5000+ (Mega)"

    df["Amount_Bucket"] = df["Amount"].apply(amount_bucket)

    recurring_kw = [
        "NETFLIX", "SPOTIFY", "HOICHOI", "CLAUDE", "ADOBE", "APPLE MEDIA",
        "APPLE SERVICE", "GOOGLE PLAY", "CHATGPT", "RENTOMOJO", "JIO",
        "BSNL", "AIRTEL", "RENT", "FLAT OWNER", "EMI", "YOUTUBE",
        "HOTSTAR", "PRIME VIDEO", "OPENAI",
    ]
    df["Is_Recurring"] = df["Description"].apply(
        lambda d: "Yes" if any(k in d.upper() for k in recurring_kw) else "No"
    )

    essential_cats = ["Housing", "Utilities", "Groceries", "Transport", "EMI Payments", "Fees & Charges"]
    df["Spend_Type"] = df["Category"].apply(
        lambda c: "Essential" if c in essential_cats else "Discretionary"
    )

    df["Cumulative_Spend"] = df.apply(
        lambda r: r["Amount"] if r["Type"] == "Debit" else 0, axis=1
    ).cumsum()

    df["Date"] = df["Date"].dt.strftime("%Y-%m-%d")

    col_order = [
        "Date", "Time", "Description", "Amount", "Type",
        "Category", "Subcategory", "Source", "Account",
        "Payment_Mode", "Bank", "UPI_ID",
        "Day", "Day_Name", "Day_of_Week", "Week_Number", "Week_Label",
        "Month", "Month_Name", "Year", "Quarter", "Year_Month",
        "Is_Weekend", "Time_Bucket",
        "Amount_Bucket", "Is_Recurring", "Spend_Type",
        "Is_Debit", "Is_Credit", "Is_Transfer", "Cumulative_Spend",
    ]
    return df[[c for c in col_order if c in df.columns]]


# ============================================================
# FILE DETECTION
# ============================================================

def detect_files(folder):
    """Return (list_of_pdfs, offline_file)."""
    all_files = os.listdir(folder)
    pdfs, offline_file = [], None

    for f in sorted(all_files):
        full_path = os.path.join(folder, f)
        if not os.path.isfile(full_path):
            continue
        f_lower = f.lower()
        if f_lower.endswith(".pdf"):
            pdfs.append(full_path)
        elif f_lower.endswith((".xlsx", ".xls")) and offline_file is None:
            offline_file = full_path
        elif f_lower.endswith(".csv") and offline_file is None:
            # Skip pipeline output files (spending_YYYYMM.csv)
            if not re.match(r"spending_\d{6}\.csv$", f_lower):
                offline_file = full_path

    return pdfs, offline_file


# ============================================================
# SUMMARY
# ============================================================

def print_summary(df):
    debits    = df[df["Type"] == "Debit"]
    credits   = df[df["Type"] == "Credit"]
    transfers = df[df["Type"] == "Transfer"]

    total_spent    = debits["Amount"].sum()
    total_received = credits["Amount"].sum()
    total_transfer = transfers["Amount"].sum()

    print("\n" + "=" * 65)
    print("  SPENDING SUMMARY")
    print("=" * 65)
    print(f"  Total transactions : {len(df)}")
    print(f"  Total spent        : Rs.{total_spent:>12,.2f}")
    print(f"  Total received     : Rs.{total_received:>12,.2f}")
    print(f"  Self transfers     : Rs.{total_transfer:>12,.2f}")
    print(f"  Net outflow        : Rs.{total_spent - total_received:>12,.2f}")

    print(f"\n  --- By Source ---")
    for src, grp in debits.groupby("Source"):
        print(f"    {src:<30} Rs.{grp['Amount'].sum():>10,.2f}  ({len(grp)} txns)")

    print(f"\n  --- Top Categories ---")
    cat_totals = debits.groupby("Category")["Amount"].sum().sort_values(ascending=False)
    for cat, amt in cat_totals.head(12).items():
        pct = amt / total_spent * 100 if total_spent else 0
        print(f"    {cat:<30} Rs.{amt:>10,.2f}  ({pct:4.1f}%)")

    uncat = debits[debits["Category"] == "Uncategorized"]
    if len(uncat):
        print(f"\n  [!] {len(uncat)} uncategorized transactions (Rs.{uncat['Amount'].sum():,.2f})")
        print(f"      Add keywords to CATEGORY_RULES at the top of the script.")
        for _, row in uncat.head(8).iterrows():
            print(f"        {row['Date']}  {row['Description']:<35}  Rs.{row['Amount']:>8,.2f}")
        if len(uncat) > 8:
            print(f"        ... and {len(uncat)-8} more")
    print("=" * 65)


# ============================================================
# MAIN
# ============================================================

def main():
    input_folder  = sys.argv[1] if len(sys.argv) >= 2 else os.environ.get(
        "DATA_FOLDER", "../../local-database/budget-tracker/monthly-data"
    )
    output_folder = sys.argv[2] if len(sys.argv) >= 3 else os.environ.get(
        "OUTPUT_FOLDER", "../../local-database/budget-tracker/output"
    )

    if not os.path.isdir(input_folder):
        print(f"ERROR: '{input_folder}' is not a valid directory.")
        sys.exit(1)

    os.makedirs(output_folder, exist_ok=True)

    print(f"\nScanning input : {os.path.abspath(input_folder)}")
    print(f"Output folder  : {os.path.abspath(output_folder)}")
    print("-" * 50)

    pdfs, offline_file = detect_files(input_folder)

    if not pdfs and not offline_file:
        print("ERROR: No PDF or spreadsheet files found.")
        sys.exit(1)

    print(f"  Found {len(pdfs)} PDF(s)  +  "
          f"{'1 offline spreadsheet' if offline_file else 'no offline spreadsheet'}")
    print()

    all_transactions = []

    for pdf_path in pdfs:
        all_transactions.extend(parse_pdf_vision(pdf_path))

    if offline_file:
        all_transactions.extend(parse_offline(offline_file))

    if not all_transactions:
        print("\nERROR: No transactions could be parsed.")
        sys.exit(1)

    df = pd.DataFrame(all_transactions)
    df = enrich_dataframe(df)

    dates      = pd.to_datetime(df["Date"])
    year_month = dates.dt.strftime("%Y%m").mode()[0]
    output_csv = os.path.join(output_folder, f"spending_{year_month}.csv")
    df.to_csv(output_csv, index=False, encoding="utf-8-sig")

    print_summary(df)
    print(f"\n  [OK] Output saved : {output_csv}")
    print(f"       {len(df)} rows x {len(df.columns)} columns")
    print(f"\n  Power BI: Get Data -> Text/CSV -> {os.path.basename(output_csv)}")
    print()


if __name__ == "__main__":
    main()
