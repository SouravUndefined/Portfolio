#!/usr/bin/env python3
"""
Unit + integration tests for the report/ package.

Tests:
  1. CSV fixture creation (realistic March 2026 data)
  2. FinancialScorer — deterministic scores, all components present
  3. RecommendationEngine — rules fire correctly, amounts are specific
  4. Orchestrator end-to-end — generates a real PDF and verifies it's readable

Run:
    python test_report.py
    python -m pytest test_report.py -v
"""

import os
import sys
import tempfile
import unittest

import pandas as pd
import numpy as np


# ── helpers ────────────────────────────────────────────────────────────────────

def make_csv(path: str) -> pd.DataFrame:
    """Build a realistic 50-row March 2026 spending dataset and write to path."""
    essential_cats = {
        "Housing", "Utilities", "Groceries", "Transport", "EMI Payments", "Fees & Charges"
    }

    rows = [
        # Housing
        ("2026-03-01", "FLAT OWNER RENT MARCH",    18000, "Debit",  "Housing",        "Rent",          "HDFC Bank",        "Debit Card",   "Yes"),
        # Groceries
        ("2026-03-02", "BIGBASKET GROCERY",         2340, "Debit",  "Groceries",      "BigBasket",     "Google Pay",       "UPI",          "No"),
        ("2026-03-10", "BLINKIT GROCERY",           1120, "Debit",  "Groceries",      "Blinkit",       "Google Pay",       "UPI",          "No"),
        ("2026-03-18", "ZEPTO GROCERY",              890, "Debit",  "Groceries",      "Zepto",         "Google Pay",       "UPI",          "No"),
        ("2026-03-24", "BIGBASKET GROCERY",         1650, "Debit",  "Groceries",      "BigBasket",     "Google Pay",       "UPI",          "No"),
        # Food & Dining
        ("2026-03-02", "ZOMATO ORDER",               480, "Debit",  "Food & Dining",  "Zomato",        "HDFC Credit Card", "Credit Card",  "No"),
        ("2026-03-04", "SWIGGY FOOD ORDER",          320, "Debit",  "Food & Dining",  "Swiggy",        "HDFC Credit Card", "Credit Card",  "No"),
        ("2026-03-06", "ZOMATO ORDER",               610, "Debit",  "Food & Dining",  "Zomato",        "HDFC Credit Card", "Credit Card",  "No"),
        ("2026-03-07", "LOCAL RESTAURANT DINNER",   1240, "Debit",  "Food & Dining",  "Restaurant",    "Google Pay",       "UPI",          "No"),
        ("2026-03-09", "SWIGGY FOOD ORDER",          290, "Debit",  "Food & Dining",  "Swiggy",        "HDFC Credit Card", "Credit Card",  "No"),
        ("2026-03-11", "ZOMATO ORDER",               520, "Debit",  "Food & Dining",  "Zomato",        "HDFC Credit Card", "Credit Card",  "No"),
        ("2026-03-13", "CAFE COFFEE DAY",            380, "Debit",  "Food & Dining",  "Cafe",          "HDFC Credit Card", "Credit Card",  "No"),
        ("2026-03-14", "SWIGGY FOOD ORDER",          445, "Debit",  "Food & Dining",  "Swiggy",        "HDFC Credit Card", "Credit Card",  "No"),
        ("2026-03-16", "ZOMATO ORDER",               670, "Debit",  "Food & Dining",  "Zomato",        "HDFC Credit Card", "Credit Card",  "No"),
        ("2026-03-19", "RESTAURANT LUNCH",           880, "Debit",  "Food & Dining",  "Restaurant",    "Google Pay",       "UPI",          "No"),
        ("2026-03-21", "SWIGGY FOOD ORDER",          355, "Debit",  "Food & Dining",  "Swiggy",        "HDFC Credit Card", "Credit Card",  "No"),
        ("2026-03-23", "ZOMATO ORDER",               495, "Debit",  "Food & Dining",  "Zomato",        "HDFC Credit Card", "Credit Card",  "No"),
        ("2026-03-25", "CAFE BRUNCH",                720, "Debit",  "Food & Dining",  "Cafe",          "Google Pay",       "UPI",          "No"),
        ("2026-03-27", "SWIGGY FOOD ORDER",          410, "Debit",  "Food & Dining",  "Swiggy",        "HDFC Credit Card", "Credit Card",  "No"),
        # Transport
        ("2026-03-03", "RAPIDO RIDE",                 89, "Debit",  "Transport",      "Rapido",        "Google Pay",       "UPI",          "No"),
        ("2026-03-05", "UBER CAB",                   340, "Debit",  "Transport",      "Uber",          "HDFC Credit Card", "Credit Card",  "No"),
        ("2026-03-08", "RAPIDO RIDE",                 65, "Debit",  "Transport",      "Rapido",        "Google Pay",       "UPI",          "No"),
        ("2026-03-12", "UBER CAB",                   210, "Debit",  "Transport",      "Uber",          "HDFC Credit Card", "Credit Card",  "No"),
        ("2026-03-17", "RAILWAYS UTS TICKET",         40, "Debit",  "Transport",      "Local Train",   "Google Pay",       "UPI",          "No"),
        ("2026-03-20", "RAPIDO RIDE",                 75, "Debit",  "Transport",      "Rapido",        "Google Pay",       "UPI",          "No"),
        ("2026-03-26", "UBER CAB",                   280, "Debit",  "Transport",      "Uber",          "HDFC Credit Card", "Credit Card",  "No"),
        # Utilities
        ("2026-03-03", "JIO PREPAID RECHARGE",       299, "Debit",  "Utilities",      "Mobile Recharge","Google Pay",      "UPI",          "Yes"),
        ("2026-03-05", "MSEDCL ELECTRICITY BILL",   1240, "Debit",  "Utilities",      "Electricity",   "Google Pay",       "UPI",          "Yes"),
        # Subscriptions
        ("2026-03-01", "NETFLIX SUBSCRIPTION",       649, "Debit",  "Subscriptions",  "Netflix",       "HDFC Credit Card", "Credit Card",  "Yes"),
        ("2026-03-01", "SPOTIFY MUSIC",              119, "Debit",  "Subscriptions",  "Spotify",       "HDFC Credit Card", "Credit Card",  "Yes"),
        ("2026-03-04", "CLAUDE AI SUBSCRIPTION",    1656, "Debit",  "Subscriptions",  "Claude AI",     "HDFC Credit Card", "Credit Card",  "Yes"),
        ("2026-03-06", "YOUTUBE PREMIUM",            139, "Debit",  "Subscriptions",  "YouTube Premium","HDFC Credit Card","Credit Card",  "Yes"),
        # Shopping
        ("2026-03-08", "AMAZON PURCHASE",           1890, "Debit",  "Shopping",       "Amazon",        "HDFC Credit Card", "Credit Card",  "No"),
        ("2026-03-15", "AMAZON PURCHASE",           3400, "Debit",  "Shopping",       "Amazon",        "HDFC Credit Card", "Credit Card",  "No"),
        ("2026-03-22", "MYNTRA CLOTHING",           2100, "Debit",  "Shopping",       "Myntra",        "HDFC Credit Card", "Credit Card",  "No"),
        ("2026-03-28", "FLIPKART PURCHASE",         1450, "Debit",  "Shopping",       "Flipkart",      "HDFC Credit Card", "Credit Card",  "No"),
        # Entertainment
        ("2026-03-08", "MOVIE TICKETS BOOKMYSHOW",   680, "Debit",  "Entertainment",  "Movies",        "HDFC Credit Card", "Credit Card",  "No"),
        ("2026-03-22", "MOVIE TICKETS BOOKMYSHOW",   760, "Debit",  "Entertainment",  "Movies",        "HDFC Credit Card", "Credit Card",  "No"),
        # Personal Care
        ("2026-03-12", "SALON HAIRCUT",              350, "Debit",  "Personal Care",  "Grooming",      "Google Pay",       "UPI",          "No"),
        # Credits / Cashback
        ("2026-03-10", "CASHBACK HDFC REWARD",       250, "Credit", "Cashback/Rewards","Cashback",     "HDFC Credit Card", "Credit Card",  "No"),
        ("2026-03-20", "ZOMATO CASHBACK",             80, "Credit", "Cashback/Rewards","Cashback",     "Google Pay",       "UPI",          "No"),
        ("2026-03-25", "AMAZON REFUND",              450, "Credit", "Cashback/Rewards","Cashback",     "HDFC Credit Card", "Credit Card",  "No"),
        # Micro / tea / snacks
        ("2026-03-03", "TEA STALL",                   20, "Debit",  "Food & Dining",  "Tea/Chai",      "Google Pay",       "UPI",          "No"),
        ("2026-03-07", "TEA STALL",                   20, "Debit",  "Food & Dining",  "Tea/Chai",      "Google Pay",       "UPI",          "No"),
        ("2026-03-11", "TEA STALL",                   20, "Debit",  "Food & Dining",  "Tea/Chai",      "Google Pay",       "UPI",          "No"),
        ("2026-03-14", "SNACKS PURCHASE",             45, "Debit",  "Food & Dining",  "Snacks/Sweets", "Google Pay",       "UPI",          "No"),
        ("2026-03-18", "TEA STALL",                   20, "Debit",  "Food & Dining",  "Tea/Chai",      "Google Pay",       "UPI",          "No"),
        ("2026-03-21", "SNACKS PURCHASE",             38, "Debit",  "Food & Dining",  "Snacks/Sweets", "Google Pay",       "UPI",          "No"),
        ("2026-03-25", "TEA STALL",                   20, "Debit",  "Food & Dining",  "Tea/Chai",      "Google Pay",       "UPI",          "No"),
        # Services
        ("2026-03-16", "SNABBIT HOME CLEANING",      799, "Debit",  "Services",       "Home Services (Snabbit)", "HDFC Credit Card", "Credit Card", "No"),
    ]

    records = []
    for (date, desc, amount, typ, cat, subcat, src, mode, recurring) in rows:
        dt = pd.Timestamp(date)
        amount_bucket = (
            "Rs.0-50 (Micro)"       if amount <=    50 else
            "Rs.51-200 (Small)"     if amount <=   200 else
            "Rs.201-500 (Medium)"   if amount <=   500 else
            "Rs.501-1000 (Large)"   if amount <=  1000 else
            "Rs.1001-5000 (Major)"  if amount <=  5000 else
            "Rs.5000+ (Mega)"
        )
        week_start = dt - pd.Timedelta(days=dt.dayofweek)
        week_end   = week_start + pd.Timedelta(days=6)
        records.append({
            "Date":          date,
            "Time":          "",
            "Description":   desc,
            "Amount":        amount,
            "Type":          typ,
            "Category":      cat,
            "Subcategory":   subcat,
            "Source":        src,
            "Account":       src,
            "Payment_Mode":  mode,
            "Bank":          src,
            "UPI_ID":        "",
            "Day":           dt.day,
            "Day_Name":      dt.day_name(),
            "Day_of_Week":   dt.dayofweek,
            "Week_Number":   int(dt.isocalendar().week),
            "Week_Label":    week_start.strftime("%d %b") + " - " + week_end.strftime("%d %b"),
            "Month":         dt.month,
            "Month_Name":    dt.strftime("%B"),
            "Year":          dt.year,
            "Quarter":       dt.quarter,
            "Year_Month":    dt.strftime("%Y-%m"),
            "Is_Weekend":    "Yes" if dt.dayofweek >= 5 else "No",
            "Time_Bucket":   "Unknown",
            "Amount_Bucket": amount_bucket,
            "Is_Recurring":  recurring,
            "Spend_Type":    "Essential" if cat in essential_cats else "Discretionary",
            "Is_Debit":      1 if typ == "Debit"    else 0,
            "Is_Credit":     1 if typ == "Credit"   else 0,
            "Is_Transfer":   1 if typ == "Transfer" else 0,
            "Cumulative_Spend": 0,
        })

    df = pd.DataFrame(records)
    df = df.sort_values("Date").reset_index(drop=True)

    cumsum = 0.0
    for i, row in df.iterrows():
        if row["Type"] == "Debit":
            cumsum += row["Amount"]
        df.at[i, "Cumulative_Spend"] = cumsum

    df.to_csv(path, index=False, encoding="utf-8-sig")
    return df


# ── test cases ─────────────────────────────────────────────────────────────────

class TestTheme(unittest.TestCase):
    def test_fmt_small(self):
        from report.theme import fmt
        self.assertEqual(fmt(500),    "Rs.500")

    def test_fmt_thousands(self):
        from report.theme import fmt
        self.assertEqual(fmt(1500),   "Rs.1.5K")

    def test_fmt_lakhs(self):
        from report.theme import fmt
        self.assertEqual(fmt(150000), "Rs.1.5L")

    def test_score_color_good(self):
        from report.theme import score_color, C
        self.assertEqual(score_color(7.5), C["success"])

    def test_score_color_warn(self):
        from report.theme import score_color, C
        self.assertEqual(score_color(5.0), C["accent"])

    def test_score_color_bad(self):
        from report.theme import score_color, C
        self.assertEqual(score_color(3.0), C["danger"])

    def test_score_grades(self):
        from report.theme import score_grade
        self.assertEqual(score_grade(90), "A")
        self.assertEqual(score_grade(72), "B")
        self.assertEqual(score_grade(60), "C")
        self.assertEqual(score_grade(45), "D")
        self.assertEqual(score_grade(30), "F")


class TestScorer(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with tempfile.NamedTemporaryFile(suffix=".csv", delete=False) as f:
            cls.csv_path = f.name
        cls.df = make_csv(cls.csv_path)
        cls.df["Date"] = pd.to_datetime(cls.df["Date"])

    @classmethod
    def tearDownClass(cls):
        os.unlink(cls.csv_path)

    def setUp(self):
        from report.scorer import FinancialScorer
        self.scorer = FinancialScorer()
        self.score  = self.scorer.compute(self.df)

    def test_score_is_integer_0_to_100(self):
        self.assertIsInstance(self.score.total, int)
        self.assertGreaterEqual(self.score.total, 0)
        self.assertLessEqual(self.score.total, 100)

    def test_out_of_ten_is_total_divided_by_10(self):
        self.assertAlmostEqual(self.score.out_of_ten, self.score.total / 10, places=1)

    def test_six_components_present(self):
        self.assertEqual(len(self.score.components), 6)

    def test_component_keys_are_unique(self):
        keys = [c.key for c in self.score.components]
        self.assertEqual(len(keys), len(set(keys)))

    def test_each_component_score_within_max(self):
        for comp in self.score.components:
            self.assertGreaterEqual(comp.score, 0)
            self.assertLessEqual(comp.score, comp.max_score)

    def test_grade_is_letter(self):
        self.assertIn(self.score.grade, ("A", "B", "C", "D", "F"))

    def test_headline_is_nonempty(self):
        self.assertGreater(len(self.score.headline), 5)

    def test_no_investment_gives_zero_investment_score(self):
        # Our fixture has no Investments category — score should be 0
        inv_comp = next(c for c in self.score.components if c.key == "investment")
        self.assertEqual(inv_comp.score, 0)

    def test_subscription_load_detected(self):
        sub_comp = next(c for c in self.score.components if c.key == "subscriptions")
        # fixture has Netflix+Spotify+Claude+YouTube = Rs.2563 on ~Rs.55K total ≈ 4.7%
        # should be "good" (3-6%) → 7 pts
        self.assertGreater(sub_comp.score, 0)

    def test_score_reproducible(self):
        score2 = self.scorer.compute(self.df)
        self.assertEqual(self.score.total, score2.total)


class TestRecommender(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with tempfile.NamedTemporaryFile(suffix=".csv", delete=False) as f:
            cls.csv_path = f.name
        cls.df = make_csv(cls.csv_path)
        cls.df["Date"] = pd.to_datetime(cls.df["Date"])

    @classmethod
    def tearDownClass(cls):
        os.unlink(cls.csv_path)

    def setUp(self):
        from report.recommender import RecommendationEngine
        self.engine = RecommendationEngine()
        self.result = self.engine.analyze(self.df)

    def test_has_at_least_one_recommendation(self):
        self.assertGreater(len(self.result.recommendations), 0)

    def test_no_more_than_six_recommendations(self):
        self.assertLessEqual(len(self.result.recommendations), 6)

    def test_invest_recommendation_fires_when_no_investments(self):
        titles = [r.title for r in self.result.recommendations]
        self.assertTrue(any("Invest" in t for t in titles),
                        f"Expected investment rec, got: {titles}")

    def test_dining_recommendation_fires(self):
        # fixture has dining >> groceries, so this should fire
        titles = [r.title for r in self.result.recommendations]
        self.assertTrue(any("Dining" in t or "dining" in t.lower() for t in titles),
                        f"Expected dining rec, got: {titles}")

    def test_each_rec_has_specifics_and_action(self):
        for rec in self.result.recommendations:
            self.assertGreater(len(rec.specifics), 10,
                               f"Rec '{rec.title}' has empty specifics")
            self.assertGreater(len(rec.action), 10,
                               f"Rec '{rec.title}' has empty action")

    def test_impact_values_are_valid(self):
        for rec in self.result.recommendations:
            self.assertIn(rec.impact, ("High", "Medium", "Low"),
                          f"Invalid impact: {rec.impact}")

    def test_missing_categories_populated(self):
        self.assertGreater(len(self.result.missing), 0)
        for m in self.result.missing:
            self.assertGreater(len(m.name), 2)
            self.assertGreater(len(m.suggested_amount), 3)

    def test_budget_targets_populated(self):
        self.assertGreater(len(self.result.budget_targets), 0)
        for t in self.result.budget_targets:
            self.assertIsInstance(t.change_pct, float)

    def test_recommendations_sorted_high_first(self):
        impact_order = {"High": 0, "Medium": 1, "Low": 2}
        orders = [impact_order[r.impact] for r in self.result.recommendations]
        self.assertEqual(orders, sorted(orders))


class TestOrchestratorEndToEnd(unittest.TestCase):
    """Generates a real PDF and checks it is a valid, non-empty file."""

    @classmethod
    def setUpClass(cls):
        cls.tmp_dir  = tempfile.mkdtemp()
        cls.csv_path = os.path.join(cls.tmp_dir, "spending_202603.csv")
        cls.pdf_path = os.path.join(cls.tmp_dir, "spending_report_202603.pdf")
        make_csv(cls.csv_path)

    @classmethod
    def tearDownClass(cls):
        import shutil
        shutil.rmtree(cls.tmp_dir, ignore_errors=True)

    def test_pdf_is_created(self):
        from report.orchestrator import ReportOrchestrator
        ReportOrchestrator().generate(self.csv_path, self.pdf_path)
        self.assertTrue(os.path.exists(self.pdf_path),
                        "PDF file was not created")

    def test_pdf_is_not_empty(self):
        size = os.path.getsize(self.pdf_path)
        self.assertGreater(size, 10_000,
                           f"PDF is suspiciously small: {size} bytes")

    def test_pdf_starts_with_pdf_magic_bytes(self):
        with open(self.pdf_path, "rb") as f:
            header = f.read(4)
        self.assertEqual(header, b"%PDF",
                         "File does not appear to be a valid PDF")

    def test_pdf_page_count(self):
        import fitz
        doc = fitz.open(self.pdf_path)
        n = len(doc)
        doc.close()
        # 1 cover + 8 data pages + 3 advisor pages = 12
        self.assertEqual(n, 12, f"Expected 12 pages, got {n}")


# ── runner ─────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    verbosity = 2
    runner = unittest.TextTestRunner(verbosity=verbosity)
    suite  = unittest.TestLoader().loadTestsFromModule(sys.modules[__name__])
    result = runner.run(suite)
    sys.exit(0 if result.wasSuccessful() else 1)
