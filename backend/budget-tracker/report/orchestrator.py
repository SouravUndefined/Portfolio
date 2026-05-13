"""
Report orchestrator — the single entry point for PDF generation.

Pipeline:
  1. Load CSV
  2. Compute financial health score  (scorer.py)
  3. Compute rule-based recommendations (recommender.py)
  4. Optionally enhance with AI narratives (ai_client.py)
  5. Render each page module in order
  6. Write the PDF

Each stage is independent and clearly named so you know exactly what is happening.
"""

from datetime import datetime
from pathlib import Path

import pandas as pd
from matplotlib.backends.backend_pdf import PdfPages

from .scorer import FinancialScorer
from .recommender import RecommendationEngine
from . import ai_client
from .pages import (
    p00_cover,
    p01_summary,
    p02_trends,
    p03_categories,
    p04_merchants,
    p05_spend_type,
    p06_insights,
    p07_advanced,
    p08_cashflow,
    p09_advisor,
)


def _load(csv_path: str) -> pd.DataFrame:
    df = pd.read_csv(csv_path)
    df["Date"] = pd.to_datetime(df["Date"])
    return df


class ReportOrchestrator:
    """Coordinates all report-generation components and writes the final PDF."""

    def generate(self, csv_path: str, output_path: str) -> None:
        print("  [1/4] Loading data ...")
        df = _load(csv_path)
        month_tag = df["Date"].dt.strftime("%B %Y").mode()[0]

        print("  [2/4] Computing financial health score ...")
        scorer = FinancialScorer()
        score  = scorer.compute(df)
        print(f"         Score: {score.total}/100  (Grade {score.grade}  —  {score.headline})")
        for comp in score.components:
            print(f"         [{comp.score:2d}/{comp.max_score}] {comp.label} — {comp.verdict}")

        print("  [3/4] Computing recommendations ...")
        engine = RecommendationEngine()
        result = engine.analyze(df)
        print(f"         {len(result.recommendations)} recommendations generated")
        for rec in result.recommendations:
            print(f"         [{rec.impact:6s}] {rec.title}")

        print("  [4/4] Requesting AI narrative enhancement ...")
        ai_data = ai_client.enhance(score, result)
        if ai_data:
            ai_client.apply_narratives(result, ai_data)
            print("         AI narratives applied.")
        else:
            print("         AI unavailable — using data-only narratives.")

        print("  Rendering PDF pages ...")
        with PdfPages(output_path) as pdf:
            print("    [1/12] Cover Page ...")
            p00_cover.render(df, pdf, score, result)

            print("    [2/12] Executive Summary ...")
            p01_summary.render(df, pdf, page_num=2)

            print("    [3/12] Spending Trends ...")
            p02_trends.render(df, pdf, page_num=3)

            print("    [4/12] Category Breakdown ...")
            p03_categories.render(df, pdf, page_num=4)

            print("    [5/12] Top Merchants ...")
            p04_merchants.render(df, pdf, page_num=5)

            print("    [6/12] Spend Type & Payment Modes ...")
            p05_spend_type.render(df, pdf, page_num=6)

            print("    [7/12] Key Insights ...")
            p06_insights.render(df, pdf, page_num=7)

            print("    [8/12] Advanced Analytics ...")
            p07_advanced.render(df, pdf, page_num=8)

            print("    [9/12] Cash Flow Profile ...")
            p08_cashflow.render(df, pdf, page_num=9)

            print("   [10/12] Financial Health Score ...")
            print("   [11/12] Recommendations ...")
            print("   [12/12] Budget Targets & Gaps ...")
            p09_advisor.render(df, pdf, score, result, ai_data, start_page=10)

            meta = pdf.infodict()
            meta["Title"]        = f"Spending Report — {month_tag}"
            meta["Author"]       = "Budget Tracker"
            meta["Subject"]      = "Personal Finance Analysis"
            meta["CreationDate"] = datetime.now()

        print(f"\n  Done — {output_path}")
        print(f"  Pages: 12  |  Score: {score.total}/100 ({score.grade})")
