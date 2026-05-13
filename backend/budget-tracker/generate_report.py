#!/usr/bin/env python3
"""
generate_report.py — public API (unchanged interface, new internals).

The actual work is done by the report/ package:
  report/scorer.py       — algorithmic 6-component financial health score
  report/recommender.py  — rule-based recommendations with specific Rs amounts
  report/ai_client.py    — AI enhancement of pre-computed narratives
  report/pages/          — individual PDF page renderers
  report/orchestrator.py — wires everything together

Usage (CLI):
    python generate_report.py /path/to/spending_202603.csv
    python generate_report.py /path/to/output/folder
"""

import os
import sys
import glob


def find_csv(path: str) -> str:
    if os.path.isfile(path) and path.endswith(".csv"):
        return path
    if os.path.isdir(path):
        files = sorted(glob.glob(os.path.join(path, "spending_*.csv")))
        if files:
            return files[-1]
    raise FileNotFoundError(f"No spending CSV found at: {path}")


def generate(csv_path: str, output_path: str) -> None:
    """Entry point called by app.py — delegates to the orchestrator."""
    from report.orchestrator import ReportOrchestrator
    ReportOrchestrator().generate(csv_path, output_path)


def main():
    from dotenv import load_dotenv
    load_dotenv()

    output_folder = os.environ.get(
        "OUTPUT_FOLDER", "../../local-database/budget-tracker/output"
    )
    target   = sys.argv[1] if len(sys.argv) >= 2 else output_folder
    csv_path = find_csv(target)

    import pandas as pd
    df        = pd.read_csv(csv_path)
    month_tag = pd.to_datetime(df["Date"]).dt.strftime("%Y%m").mode()[0]
    out_pdf   = os.path.join(output_folder, f"spending_report_{month_tag}.pdf")

    print(f"  Source  : {csv_path}")
    print(f"  Records : {len(df)} rows")
    print(f"  Output  : {out_pdf}")
    print()

    generate(csv_path, out_pdf)


if __name__ == "__main__":
    main()
