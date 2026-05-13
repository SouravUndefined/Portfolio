"""
Rule-based recommendation engine.

Every recommendation is computed from real numbers in the data — not generated
by a language model. Each one carries a specific Rs. impact and an exact action.
The AI client later adds a polished narrative sentence on top of these facts.
"""

from dataclasses import dataclass, field
from typing import List, Optional

import pandas as pd

from .theme import fmt


@dataclass
class Recommendation:
    id: int
    title: str
    specifics: str          # one-line data fact (amounts, percentages)
    action: str             # one concrete step with a specific number
    impact: str             # "High" | "Medium" | "Low"
    monthly_impact: float   # estimated Rs/month saving (positive = saving)
    category: str
    narrative: str = ""     # filled in by AIClient if available


@dataclass
class MissingCategory:
    name: str
    why: str
    suggested_amount: str


@dataclass
class BudgetTarget:
    category: str
    current: str
    suggested: str
    change_pct: float       # negative = reduction, positive = increase


@dataclass
class RecommendationResult:
    recommendations: List[Recommendation] = field(default_factory=list)
    missing: List[MissingCategory] = field(default_factory=list)
    budget_targets: List[BudgetTarget] = field(default_factory=list)
    positive_habits: List[str] = field(default_factory=list)


class RecommendationEngine:
    """
    Analyses spending data and returns specific, quantified recommendations.
    Each rule either fires or doesn't — no generic advice.
    """

    def analyze(self, df: pd.DataFrame) -> RecommendationResult:
        debits = df[df["Type"] == "Debit"].copy()
        debits["Date"] = pd.to_datetime(debits["Date"])
        total = debits["Amount"].sum()
        if total == 0:
            return RecommendationResult()

        recs: List[Recommendation] = []
        rid = 1

        # ── Rule 1: Dining out vs grocery balance ──────────────────────────────
        dining  = debits[debits["Category"] == "Food & Dining"]["Amount"].sum()
        grocery = debits[debits["Category"] == "Groceries"]["Amount"].sum()
        food_total = dining + grocery
        if food_total > 0 and dining / food_total > 0.50:
            dining_pct = dining / food_total * 100
            saving = dining * 0.25
            recs.append(Recommendation(
                id=rid, category="Food & Dining",
                title="Cut Dining Out by 25%",
                specifics=(
                    f"Rs.{dining:,.0f} on restaurants ({dining_pct:.0f}% of food budget) "
                    f"vs Rs.{grocery:,.0f} on groceries — benchmark is <40% dining"
                ),
                action=(
                    f"Set a Rs.{dining * 0.75:,.0f}/month cap on Swiggy/Zomato "
                    f"(current: Rs.{dining:,.0f})"
                ),
                monthly_impact=saving,
                impact="High" if dining > total * 0.12 else "Medium",
            ))
            rid += 1

        # ── Rule 2: Subscription overload ─────────────────────────────────────
        # Only count discretionary recurring payments — not rent/utilities
        essential_cats = {
            "Housing", "Utilities", "Groceries", "Transport",
            "EMI Payments", "Fees & Charges", "Insurance", "Investments",
        }
        subs = debits[
            (debits["Is_Recurring"] == "Yes") &
            (~debits["Category"].isin(essential_cats))
        ]
        sub_total = subs["Amount"].sum()
        sub_pct = sub_total / total * 100
        if sub_pct > 5:
            top_subs = (
                subs.groupby("Description")["Amount"].sum()
                .nlargest(5)
            )
            sub_list = ", ".join(
                f"{d} Rs.{a:,.0f}" for d, a in top_subs.items()
            )
            n_subs = subs["Description"].nunique()
            saving = sub_total * 0.30
            recs.append(Recommendation(
                id=rid, category="Subscriptions",
                title=f"Audit {n_subs} Subscriptions",
                specifics=(
                    f"Rs.{sub_total:,.0f}/month ({sub_pct:.1f}% of spend) across {n_subs} services: "
                    f"{sub_list}"
                ),
                action=(
                    f"Cancel 2-3 unused services — target Rs.{sub_total * 0.70:,.0f}/month "
                    f"(saves Rs.{saving:,.0f}/month = Rs.{saving * 12:,.0f}/year)"
                ),
                monthly_impact=saving,
                impact="High" if sub_pct > 10 else "Medium",
            ))
            rid += 1

        # ── Rule 3: No investment spending ────────────────────────────────────
        inv_cats = {"Investments", "Insurance", "Savings", "SIP", "Mutual Fund", "PPF"}
        has_investment = debits["Category"].isin(inv_cats).any()
        if not has_investment:
            target = max(min(total * 0.20, 10_000), 500)
            recs.append(Recommendation(
                id=rid, category="Investments",
                title="Start Investing — Zero Found",
                specifics="No investment, SIP, or insurance payments detected this month",
                action=(
                    f"Set up a Rs.{target:,.0f}/month SIP in a NIFTY 50 index fund "
                    f"(10-15 year horizon compounds to Rs.{target * 200:,.0f}+)"
                ),
                monthly_impact=0,   # not a saving; it's a reallocation priority
                impact="High",
            ))
            rid += 1

        # ── Rule 4: Weekend spending spike ────────────────────────────────────
        wknd = debits[debits["Is_Weekend"] == "Yes"]
        wkdy = debits[debits["Is_Weekend"] == "No"]
        wknd_days = max(wknd["Date"].nunique(), 1)
        wkdy_days = max(wkdy["Date"].nunique(), 1)
        wknd_avg = wknd["Amount"].sum() / wknd_days
        wkdy_avg = wkdy["Amount"].sum() / wkdy_days
        if wknd_days >= 2 and wknd_avg > wkdy_avg * 1.6:
            excess_per_wknd_day = wknd_avg - wkdy_avg * 1.3
            monthly_excess = excess_per_wknd_day * wknd_days
            recs.append(Recommendation(
                id=rid, category="Lifestyle",
                title="Weekend Spending Spikes",
                specifics=(
                    f"Avg Rs.{wknd_avg:,.0f}/weekend day vs Rs.{wkdy_avg:,.0f}/weekday "
                    f"({wknd_avg / wkdy_avg:.1f}x more on weekends)"
                ),
                action=(
                    f"Set a weekend daily budget of Rs.{wkdy_avg * 1.3:,.0f} "
                    f"(vs current avg Rs.{wknd_avg:,.0f})"
                ),
                monthly_impact=monthly_excess * 0.4,
                impact="Medium",
            ))
            rid += 1

        # ── Rule 5: Single merchant dominance ─────────────────────────────────
        top_m = debits.groupby("Description")["Amount"].sum().nlargest(1)
        if len(top_m):
            m_name, m_amt = top_m.index[0], top_m.iloc[0]
            m_pct = m_amt / total * 100
            if m_pct > 15:
                saving = m_amt * 0.20
                recs.append(Recommendation(
                    id=rid, category="Spending Concentration",
                    title=f"Over-reliance on {m_name[:28]}",
                    specifics=(
                        f"Rs.{m_amt:,.0f} ({m_pct:.1f}% of total spend) "
                        f"at a single merchant — high concentration risk"
                    ),
                    action=(
                        f"Diversify: reduce {m_name[:28]} spend by Rs.{saving:,.0f} "
                        f"to Rs.{m_amt - saving:,.0f}/month"
                    ),
                    monthly_impact=saving,
                    impact="High" if m_pct > 25 else "Medium",
                ))
                rid += 1

        # ── Rule 6: Cash/micro transaction clutter ────────────────────────────
        micro = debits[debits["Amount"] <= 50]
        micro_count = len(micro)
        if micro_count >= 10:
            micro_total = micro["Amount"].sum()
            recs.append(Recommendation(
                id=rid, category="Micro Spends",
                title=f"Consolidate {micro_count} Micro Transactions",
                specifics=(
                    f"{micro_count} transactions under Rs.50 "
                    f"totalling Rs.{micro_total:,.0f} — each one erodes tracking clarity"
                ),
                action=(
                    "Use a Rs.200-500 weekly cash envelope for small daily buys instead of "
                    "individual UPI payments — fewer entries, same spending"
                ),
                monthly_impact=micro_total * 0.10,
                impact="Low",
            ))
            rid += 1

        # Sort: High impact first, then by Rs. impact descending
        impact_order = {"High": 0, "Medium": 1, "Low": 2}
        recs.sort(key=lambda r: (impact_order.get(r.impact, 3), -r.monthly_impact))

        # ── Missing categories ─────────────────────────────────────────────────
        missing = self._find_missing(debits, total)

        # ── Budget targets for next month ─────────────────────────────────────
        budget_targets = self._compute_budget_targets(debits, total)

        # ── Positive habits ───────────────────────────────────────────────────
        positive = self._find_positives(debits, total, has_investment)

        return RecommendationResult(
            recommendations=recs[:6],
            missing=missing,
            budget_targets=budget_targets,
            positive_habits=positive,
        )

    def _find_missing(self, debits: pd.DataFrame, total: float) -> List[MissingCategory]:
        cats = set(debits["Category"].unique())
        missing = []

        if not {"Investments", "Savings", "SIP", "PPF", "Mutual Fund"} & cats:
            missing.append(MissingCategory(
                name="Investments / SIP",
                why="No SIP, PPF, or mutual fund activity — compounding requires consistency",
                suggested_amount=f"Rs.{min(total * 0.20, 10000):,.0f}/month (20% of spend)",
            ))

        if "Insurance" not in cats:
            has_health_kw = debits["Description"].str.upper().str.contains(
                "HEALTH|MEDICLAIM|INSURANCE|LIC|LIFE|TERM", na=False, regex=True
            ).any()
            if not has_health_kw:
                missing.append(MissingCategory(
                    name="Health Insurance",
                    why="Medical emergencies without cover can wipe out savings instantly",
                    suggested_amount="Rs.500-1,500/month (term health plan)",
                ))

        if "Healthcare" not in cats and "Health" not in cats:
            has_medical = debits["Description"].str.upper().str.contains(
                "HOSPITAL|PHARMACY|CLINIC|DOCTOR|DIAGNOSTIC|MEDIC", na=False, regex=True
            ).any()
            if not has_medical:
                missing.append(MissingCategory(
                    name="Healthcare / Emergency Fund",
                    why="Even Rs.500/month into a liquid fund builds a critical safety net",
                    suggested_amount=f"Rs.{max(500, int(total * 0.05)):,.0f}/month into liquid fund",
                ))

        return missing[:4]

    def _compute_budget_targets(self, debits: pd.DataFrame, total: float) -> List[BudgetTarget]:
        cat_totals = debits.groupby("Category")["Amount"].sum().nlargest(6)
        targets = []

        # Category-specific reduction multipliers (if over benchmark)
        reductions = {
            "Food & Dining": 0.80,     # aim for 20% cut
            "Shopping":      0.75,     # aim for 25% cut
            "Entertainment": 0.75,
            "Subscriptions": 0.70,
            "Transport":     1.00,     # keep as-is (usually essential)
            "Groceries":     1.05,     # slight increase encouraged
            "Housing":       1.00,
            "Utilities":     1.00,
        }

        for cat, current_amt in cat_totals.items():
            factor = reductions.get(cat, 0.90)
            suggested_amt = current_amt * factor
            change_pct = (suggested_amt - current_amt) / current_amt * 100
            targets.append(BudgetTarget(
                category=cat,
                current=fmt(current_amt),
                suggested=fmt(suggested_amt),
                change_pct=change_pct,
            ))

        return targets

    def _find_positives(
        self, debits: pd.DataFrame, total: float, has_investment: bool
    ) -> List[str]:
        positives = []

        if has_investment:
            positives.append("Consistent investment / insurance payments detected")

        grocery = debits[debits["Category"] == "Groceries"]["Amount"].sum()
        dining = debits[debits["Category"] == "Food & Dining"]["Amount"].sum()
        if grocery > 0 and (dining == 0 or grocery / (grocery + dining) > 0.5):
            positives.append("Mostly cooking at home — good grocery-to-dining ratio")

        sub_total = debits[debits["Is_Recurring"] == "Yes"]["Amount"].sum()
        if sub_total / total < 0.05:
            positives.append("Subscription spending is well under control (<5%)")

        daily = debits.groupby("Date")["Amount"].sum()
        if len(daily) > 3 and daily.std() / daily.mean() < 0.8:
            positives.append("Very consistent daily spending — no major surprise spikes")

        essential_cats = {
            "Housing", "Utilities", "Groceries", "Transport", "EMI Payments"
        }
        ess_pct = debits[debits["Category"].isin(essential_cats)]["Amount"].sum() / total * 100
        if ess_pct >= 50:
            positives.append(
                f"{ess_pct:.0f}% spent on essentials — spending priorities are sound"
            )

        return positives[:3]
