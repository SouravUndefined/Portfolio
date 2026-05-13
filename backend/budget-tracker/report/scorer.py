"""
Algorithmic financial health scorer.

Produces a deterministic score from 0-100 (shown as X/10) by evaluating
six independent components against the user's actual spending data.
No LLM involved — every point is earned or lost by a measurable rule.
"""

from dataclasses import dataclass, field
from typing import List

import numpy as np
import pandas as pd

from .theme import C, score_color, score_grade


@dataclass
class ScoreComponent:
    key: str
    label: str
    score: int
    max_score: int
    detail: str        # explains why this score was awarded
    verdict: str       # "excellent" | "good" | "warning" | "poor"

    @property
    def pct(self) -> float:
        return self.score / self.max_score if self.max_score else 0.0

    @property
    def color(self) -> str:
        if self.pct >= 0.75: return C["success"]
        if self.pct >= 0.50: return C["accent"]
        return C["danger"]


@dataclass
class ScoreResult:
    total: int                              # 0-100
    components: List[ScoreComponent] = field(default_factory=list)

    @property
    def out_of_ten(self) -> float:
        return round(self.total / 10, 1)

    @property
    def color(self) -> str:
        return score_color(self.out_of_ten)

    @property
    def grade(self) -> str:
        return score_grade(self.total)

    @property
    def headline(self) -> str:
        if self.total >= 85: return "Excellent financial discipline"
        if self.total >= 70: return "Good habits with room to improve"
        if self.total >= 55: return "Moderate control — focus needed"
        if self.total >= 40: return "Several areas need attention"
        return "Significant financial gaps detected"


class FinancialScorer:
    """
    Six scoring components — each measured independently, summed to 100.

    Component        Max   What it measures
    ─────────────────────────────────────────────────────────────────
    Investment       20    Any savings/insurance/investment spending
    Discretionary    25    % of spend that is wants vs needs
    Food Efficiency  15    Home cooking ratio (groceries vs dining out)
    Subscriptions    10    Subscription load as % of total spend
    Consistency      15    Daily spend variance (coefficient of variation)
    Peak Control     15    Largest single-day spend vs monthly total
    """

    def compute(self, df: pd.DataFrame) -> ScoreResult:
        debits = df[df["Type"] == "Debit"].copy()
        total = debits["Amount"].sum()
        if total == 0:
            return ScoreResult(total=50, components=[])

        debits["Date"] = pd.to_datetime(debits["Date"])

        components = [
            self._investment_readiness(debits, total),
            self._discretionary_control(debits, total),
            self._food_efficiency(debits),
            self._subscription_discipline(debits, total),
            self._spending_consistency(debits),
            self._peak_day_control(debits, total),
        ]

        raw = sum(c.score for c in components)
        return ScoreResult(total=min(raw, 100), components=components)

    # ── component scorers ──────────────────────────────────────────────────────

    def _investment_readiness(self, debits: pd.DataFrame, total: float) -> ScoreComponent:
        """0-20 pts: Does the person invest or have insurance?"""
        inv_cats = {"Investments", "Savings", "Insurance", "SIP", "Mutual Fund", "PPF"}
        health_kw = (
            "HEALTH", "MEDICLAIM", "INSURANCE", "LIC", "HDFC LIFE",
            "MAX LIFE", "TERM PLAN", "SBI LIFE", "BAJAJ ALLIANZ"
        )
        inv_cats_lower = {c.lower() for c in inv_cats}
        has_inv = debits["Category"].str.lower().isin(inv_cats_lower).any()
        has_health = debits["Description"].str.upper().str.contains(
            "|".join(health_kw), na=False, regex=True
        ).any()

        score = (12 if has_inv else 0) + (8 if has_health else 0)

        if has_inv and has_health:
            verdict, detail = "excellent", "Investment and health insurance spending detected"
        elif has_inv:
            verdict, detail = "good", "Investment spending found — add health insurance"
        elif has_health:
            verdict, detail = "good", "Health insurance found — add SIP or savings"
        else:
            verdict = "poor"
            detail = "No investment or insurance payments detected — biggest financial gap"

        return ScoreComponent("investment", "Investment Readiness", score, 20, detail, verdict)

    def _discretionary_control(self, debits: pd.DataFrame, total: float) -> ScoreComponent:
        """0-25 pts: What fraction of spending is discretionary?"""
        essential_cats = {
            "Housing", "Utilities", "Groceries", "Transport",
            "EMI Payments", "Fees & Charges", "Insurance", "Investments",
        }
        disc = debits[~debits["Category"].isin(essential_cats)]["Amount"].sum()
        disc_pct = disc / total * 100

        if disc_pct <= 25:   score, verdict = 25, "excellent"
        elif disc_pct <= 35: score, verdict = 18, "good"
        elif disc_pct <= 45: score, verdict = 12, "warning"
        elif disc_pct <= 55: score, verdict = 6,  "warning"
        else:                score, verdict = 0,  "poor"

        detail = f"{disc_pct:.0f}% of spend is discretionary — target <35%"
        return ScoreComponent("discretionary", "Discretionary Control", score, 25, detail, verdict)

    def _food_efficiency(self, debits: pd.DataFrame) -> ScoreComponent:
        """0-15 pts: Are they cooking at home or eating out every meal?"""
        dining = debits[debits["Category"] == "Food & Dining"]["Amount"].sum()
        grocery = debits[debits["Category"] == "Groceries"]["Amount"].sum()
        food_total = dining + grocery

        if food_total == 0:
            return ScoreComponent("food", "Food Efficiency", 8, 15,
                                  "No food transactions found", "good")

        dining_pct = dining / food_total * 100

        if dining_pct <= 30:   score, verdict = 15, "excellent"
        elif dining_pct <= 50: score, verdict = 11, "good"
        elif dining_pct <= 70: score, verdict = 6,  "warning"
        else:                  score, verdict = 0,  "poor"

        detail = (
            f"{dining_pct:.0f}% of food spend is dining out "
            f"(Rs.{dining:,.0f} restaurants vs Rs.{grocery:,.0f} groceries) — target <40%"
        )
        return ScoreComponent("food", "Food Efficiency", score, 15, detail, verdict)

    def _subscription_discipline(self, debits: pd.DataFrame, total: float) -> ScoreComponent:
        """0-10 pts: Are discretionary subscriptions eating a disproportionate share?

        Rent and utilities are recurring but expected — only count genuinely discretionary
        recurring payments (streaming, SaaS, memberships) against this score.
        """
        essential_cats = {
            "Housing", "Utilities", "Groceries", "Transport",
            "EMI Payments", "Fees & Charges", "Insurance", "Investments",
        }
        disc_recurring = debits[
            (debits["Is_Recurring"] == "Yes") &
            (~debits["Category"].isin(essential_cats))
        ]
        sub_total = disc_recurring["Amount"].sum()
        sub_pct   = sub_total / total * 100

        if sub_pct <= 3:    score, verdict = 10, "excellent"
        elif sub_pct <= 6:  score, verdict = 7,  "good"
        elif sub_pct <= 10: score, verdict = 4,  "warning"
        elif sub_pct <= 15: score, verdict = 1,  "poor"
        else:               score, verdict = 0,  "poor"

        n_subs = disc_recurring["Description"].nunique()
        detail = (
            f"Rs.{sub_total:,.0f}/month across {n_subs} discretionary subscriptions "
            f"({sub_pct:.1f}% of total) — target <5%"
        )
        return ScoreComponent("subscriptions", "Subscription Load", score, 10, detail, verdict)

    def _spending_consistency(self, debits: pd.DataFrame) -> ScoreComponent:
        """0-15 pts: Is daily spending consistent or wildly volatile?"""
        daily = debits.groupby("Date")["Amount"].sum()
        if len(daily) < 3:
            return ScoreComponent("consistency", "Spending Consistency", 10, 15,
                                  "Too few data points to assess consistency", "good")

        cv = daily.std() / daily.mean() if daily.mean() > 0 else 999

        if cv <= 0.8:   score, verdict = 15, "excellent"
        elif cv <= 1.2: score, verdict = 11, "good"
        elif cv <= 1.8: score, verdict = 6,  "warning"
        else:           score, verdict = 2,  "poor"

        detail = (
            f"Daily spend std dev is {cv:.1f}x the mean — "
            + ("very consistent" if cv <= 0.8 else
               "mostly steady" if cv <= 1.2 else
               "somewhat volatile" if cv <= 1.8 else
               "highly volatile (review spike days)")
        )
        return ScoreComponent("consistency", "Spending Consistency", score, 15, detail, verdict)

    def _peak_day_control(self, debits: pd.DataFrame, total: float) -> ScoreComponent:
        """0-15 pts: Does one bad day dominate the whole month?"""
        daily = debits.groupby("Date")["Amount"].sum()
        if len(daily) == 0:
            return ScoreComponent("peak", "Peak Day Control", 15, 15, "No daily data", "excellent")

        peak = daily.max()
        peak_pct = peak / total * 100
        peak_date = daily.idxmax()

        if peak_pct <= 10:   score, verdict = 15, "excellent"
        elif peak_pct <= 20: score, verdict = 10, "good"
        elif peak_pct <= 30: score, verdict = 5,  "warning"
        else:                score, verdict = 0,  "poor"

        date_str = peak_date.strftime("%d %b") if hasattr(peak_date, "strftime") else str(peak_date)
        detail = (
            f"Largest day: {date_str} — Rs.{peak:,.0f} ({peak_pct:.1f}% of monthly total) — target <10%"
        )
        return ScoreComponent("peak", "Peak Day Control", score, 15, detail, verdict)
