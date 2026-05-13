"""
Cover page — dramatic dark-theme opener with arc score gauge and key stats.
"""

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from matplotlib.patches import FancyBboxPatch
import pandas as pd

from ..theme import C, CAT_COLORS, fmt, score_color, score_arc_gauge
from ..scorer import ScoreResult
from ..recommender import RecommendationResult


def render(df: pd.DataFrame, pdf, score: ScoreResult, result: RecommendationResult) -> None:
    fig = plt.figure(figsize=(11.69, 8.27))
    fig.patch.set_facecolor("#0F172A")   # deep navy

    month_label = df["Date"].dt.strftime("%B %Y").mode()[0]
    d = df[df["Type"] == "Debit"]
    c = df[df["Type"] == "Credit"]
    total_spent    = d["Amount"].sum()
    total_received = c["Amount"].sum()
    n_txns         = len(df)
    top_cat        = d.groupby("Category")["Amount"].sum().idxmax() if len(d) else "—"

    sc = score_color(score.out_of_ten)

    # ── subtle diagonal stripe texture (decorative) ───────────────────────────
    ax_bg = fig.add_axes([0, 0, 1, 1])
    ax_bg.set_facecolor("#0F172A")
    ax_bg.axis("off")
    for i in np.arange(-2, 4, 0.18):
        ax_bg.plot([i, i + 2], [0, 1.5], color="white", alpha=0.025,
                   linewidth=18, transform=ax_bg.transAxes)

    # ── left panel ────────────────────────────────────────────────────────────
    ax_bg.text(0.04, 0.90, "PERSONAL SPENDING", transform=ax_bg.transAxes,
               fontsize=11, color="white", alpha=0.55, fontweight="bold",
               va="top")
    ax_bg.text(0.04, 0.81, "REPORT", transform=ax_bg.transAxes,
               fontsize=42, color="white", fontweight="bold", va="top")
    ax_bg.text(0.04, 0.61, month_label, transform=ax_bg.transAxes,
               fontsize=24, color=sc, fontweight="bold", va="top")

    # divider line
    ax_bg.plot([0.04, 0.38], [0.56, 0.56], color="white", alpha=0.15,
               linewidth=1, transform=ax_bg.transAxes)

    # brief descriptor
    ax_bg.text(0.04, 0.51, "Algorithmic financial health analysis\nbased on your actual transaction data.",
               transform=ax_bg.transAxes, fontsize=9.5, color="white", alpha=0.55,
               va="top", linespacing=1.6)

    # grade badge
    grade_ax = fig.add_axes([0.04, 0.24, 0.10, 0.16])
    grade_ax.axis("off"); grade_ax.set_xlim(0, 1); grade_ax.set_ylim(0, 1)
    badge = FancyBboxPatch((0.05, 0.05), 0.90, 0.90,
                           boxstyle="round,pad=0.08",
                           facecolor=sc, edgecolor="none", zorder=1)
    grade_ax.add_patch(badge)
    grade_ax.text(0.5, 0.58, score.grade, ha="center", va="center",
                  fontsize=30, fontweight="bold", color="white", zorder=2)
    grade_ax.text(0.5, 0.18, "GRADE", ha="center", va="center",
                  fontsize=7, color="white", alpha=0.85, fontweight="bold", zorder=2)

    ax_bg.text(0.18, 0.32, score.headline, transform=ax_bg.transAxes,
               fontsize=9.5, color="white", alpha=0.70, va="center")

    # ── centre: arc gauge ─────────────────────────────────────────────────────
    ax_gauge = fig.add_axes([0.37, 0.22, 0.28, 0.58])
    ax_gauge.set_facecolor("none")
    score_arc_gauge(ax_gauge, score.out_of_ten, sc)
    ax_gauge.text(0, -0.22, "Financial Health Score", ha="center", va="center",
                  fontsize=10, color="white", alpha=0.65,
                  transform=ax_gauge.transData)

    # score numeric ring label
    ax_bg.text(0.505, 0.10, f"{score.total} / 100 points",
               transform=ax_bg.transAxes, fontsize=9,
               color=sc, fontweight="bold", ha="center", va="center")

    # ── right panel: 4 KPI chips ──────────────────────────────────────────────
    kpis = [
        ("Total Spent",     fmt(total_spent),     C["danger"]),
        ("Total Credits",   fmt(total_received),  C["success"]),
        ("Transactions",    str(n_txns),          C["primary"]),
        ("Top Category",    top_cat[:18],          C["secondary"]),
    ]
    for i, (label, value, color) in enumerate(kpis):
        y_pos = 0.72 - i * 0.175
        chip_ax = fig.add_axes([0.70, y_pos, 0.26, 0.14])
        chip_ax.axis("off"); chip_ax.set_xlim(0, 1); chip_ax.set_ylim(0, 1)

        bg = FancyBboxPatch((0.02, 0.06), 0.96, 0.88,
                            boxstyle="round,pad=0.05",
                            facecolor=color + "28", edgecolor=color + "66",
                            linewidth=1.2, zorder=1)
        chip_ax.add_patch(bg)

        left_bar = FancyBboxPatch((0.02, 0.06), 0.045, 0.88,
                                  boxstyle="round,pad=0.01",
                                  facecolor=color, edgecolor="none", zorder=2)
        chip_ax.add_patch(left_bar)

        chip_ax.text(0.13, 0.68, label, transform=chip_ax.transAxes,
                     fontsize=7.5, color="white", alpha=0.65, va="top")
        chip_ax.text(0.13, 0.28, value, transform=chip_ax.transAxes,
                     fontsize=13, fontweight="bold", color="white", va="top")

    # ── bottom tagline ─────────────────────────────────────────────────────────
    ax_bg.plot([0, 1], [0.055, 0.055], color="white", alpha=0.08,
               linewidth=1, transform=ax_bg.transAxes)
    ax_bg.text(0.5, 0.028, "Generated by Budget Tracker  ·  Scores computed algorithmically from 6 independent signals",
               transform=ax_bg.transAxes, fontsize=7.5,
               color="white", alpha=0.35, ha="center", va="center")

    pdf.savefig(fig, bbox_inches="tight")
    plt.close(fig)
