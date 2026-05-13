"""
Pages 10-12: Financial Health Score, Recommendations, Budget & Gaps
"""

import textwrap
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch
import pandas as pd

from ..theme import (
    C, CAT_COLORS, IMPACT_COLORS, apply_style, new_figure,
    page_header_band, page_footer, fmt, score_arc_gauge,
)
from ..scorer import ScoreResult
from ..recommender import RecommendationResult


# ── PAGE 10: Financial Health Score ───────────────────────────────────────────

def _page_score(df, pdf, score: ScoreResult, result: RecommendationResult,
                ai_verdict: str, page_num: int) -> None:
    apply_style()
    fig = new_figure()
    month_label = df["Date"].dt.strftime("%B %Y").mode()[0]
    page_header_band(fig, "Financial Health Score", month_label, color="#1E293B")
    page_footer(fig, page_num)

    # ── arc gauge (left) ──────────────────────────────────────────────────────
    ax_gauge = fig.add_axes([0.03, 0.54, 0.28, 0.36])
    ax_gauge.set_facecolor(C["card"])
    for spine in ax_gauge.spines.values():
        spine.set_visible(False)
    score_arc_gauge(ax_gauge, score.out_of_ten, score.color)

    # grade badge below the gauge
    ax_gauge.text(0, -0.20, f"Grade  {score.grade}", ha="center", va="center",
                  fontsize=13, fontweight="bold", color=score.color,
                  transform=ax_gauge.transData)

    # ── headline + verdict (right of gauge) ───────────────────────────────────
    ax_v = fig.add_axes([0.34, 0.67, 0.62, 0.22])
    ax_v.axis("off"); ax_v.set_xlim(0, 1); ax_v.set_ylim(0, 1)
    verdict_bg = FancyBboxPatch(
        (0, 0), 1, 1,
        boxstyle="round,pad=0.03",
        facecolor=score.color + "18", edgecolor=score.color + "55",
        linewidth=1, transform=ax_v.transAxes, zorder=1,
    )
    ax_v.add_patch(verdict_bg)
    ax_v.text(0.03, 0.82, score.headline,
              transform=ax_v.transAxes, fontsize=11, fontweight="bold",
              color=score.color, va="top")
    body = ai_verdict or "Score derived from 6 independent spending signals. See component breakdown below."
    ax_v.text(0.03, 0.48, textwrap.fill(body, width=90),
              transform=ax_v.transAxes, fontsize=8.5, color=C["body"],
              va="top", linespacing=1.5, style="italic")
    ax_v.text(0.03, 0.08, f"{score.total} / 100 points",
              transform=ax_v.transAxes, fontsize=9, fontweight="bold",
              color=score.color, va="bottom")

    # ── component breakdown bars ──────────────────────────────────────────────
    ax_bars = fig.add_axes([0.34, 0.36, 0.62, 0.28])
    ax_bars.set_facecolor(C["card"])
    for spine in ax_bars.spines.values():
        spine.set_visible(False)
    ax_bars.axis("off")
    ax_bars.set_xlim(-0.05, 1.12); ax_bars.set_ylim(-0.05, 1.05)

    comps = score.components
    n = len(comps)
    y_positions = np.linspace(0.90, 0.08, n)
    bar_h = 0.08

    for comp, y in zip(comps, y_positions):
        pct = comp.score / comp.max_score
        # track
        ax_bars.barh(y, 1.0, height=bar_h, color="#E2E8F0", left=0, zorder=1)
        # fill
        ax_bars.barh(y, pct, height=bar_h, color=comp.color, left=0, zorder=2)
        # label
        ax_bars.text(-0.02, y, comp.label, ha="right", va="center",
                     fontsize=7.5, color=C["text"], fontweight="bold")
        ax_bars.text(1.02, y, f"{comp.score}/{comp.max_score}",
                     ha="left", va="center", fontsize=7.5,
                     color=comp.color, fontweight="bold")

    ax_bars.set_title("Score Breakdown", fontweight="bold", fontsize=9.5,
                      color=C["text"], pad=4, loc="left")

    # ── component details grid ────────────────────────────────────────────────
    ax_det = fig.add_axes([0.03, 0.10, 0.92, 0.24])
    ax_det.axis("off"); ax_det.set_xlim(0, 1); ax_det.set_ylim(0, 1)
    ax_det.set_facecolor("none")
    ax_det.set_title("What each component measures", fontweight="bold",
                     fontsize=9, color=C["muted"], pad=4, loc="left")

    cols = 2
    for i, comp in enumerate(comps):
        col = i % cols
        row = i // cols
        x0 = 0.02 + col * 0.50
        y0 = 0.92 - row * 0.34

        chip = FancyBboxPatch(
            (x0, y0 - 0.28), 0.46, 0.30,
            boxstyle="round,pad=0.02",
            facecolor=C["card"], edgecolor=comp.color + "55",
            linewidth=1, transform=ax_det.transAxes, zorder=1,
        )
        ax_det.add_patch(chip)
        ax_det.text(x0 + 0.02, y0 - 0.02,
                    f"[{comp.score}/{comp.max_score}]  {comp.label}",
                    transform=ax_det.transAxes,
                    fontsize=7.5, fontweight="bold", color=comp.color, va="top")
        ax_det.text(x0 + 0.02, y0 - 0.12,
                    textwrap.fill(comp.detail, width=58),
                    transform=ax_det.transAxes,
                    fontsize=7, color=C["body"], va="top", linespacing=1.3)

    # ── positive habits strip ─────────────────────────────────────────────────
    if result.positive_habits:
        ax_pos = fig.add_axes([0.03, 0.54, 0.28, 0.08])
        ax_pos.axis("off"); ax_pos.set_xlim(0, 1); ax_pos.set_ylim(0, 1)
        bg = FancyBboxPatch(
            (0, 0), 1, 1, boxstyle="round,pad=0.04",
            facecolor=C["success"] + "22", edgecolor=C["success"] + "66",
            linewidth=1, transform=ax_pos.transAxes,
        )
        ax_pos.add_patch(bg)
        habit_lines = "\n".join(f"✓  {h}" for h in result.positive_habits)
        ax_pos.text(0.06, 0.92, "DOING WELL", transform=ax_pos.transAxes,
                    fontsize=7, fontweight="bold", color=C["success"], va="top")
        ax_pos.text(0.06, 0.65, habit_lines, transform=ax_pos.transAxes,
                    fontsize=7, color=C["success"], va="top", linespacing=1.5)

    pdf.savefig(fig, bbox_inches="tight")
    plt.close(fig)


# ── PAGE 11: Recommendations ──────────────────────────────────────────────────

def _rec_card(fig, x, y, w, h, rec, index: int) -> None:
    ax = fig.add_axes([x, y, w, h])
    ax.axis("off"); ax.set_xlim(0, 1); ax.set_ylim(0, 1)

    ic = IMPACT_COLORS.get(rec.impact, C["accent"])

    # card background
    card = FancyBboxPatch(
        (0, 0), 1, 1, boxstyle="round,pad=0.03",
        facecolor=C["card"], edgecolor=C["border"], linewidth=0.8,
        transform=ax.transAxes, zorder=1,
    )
    ax.add_patch(card)

    # left colour accent bar
    accent = FancyBboxPatch(
        (0, 0), 0.022, 1, boxstyle="round,pad=0.01",
        facecolor=ic, edgecolor="none",
        transform=ax.transAxes, zorder=2,
    )
    ax.add_patch(accent)

    # impact badge (top-right pill)
    badge = FancyBboxPatch(
        (0.80, 0.78), 0.185, 0.17,
        boxstyle="round,pad=0.02",
        facecolor=ic + "28", edgecolor=ic + "88",
        linewidth=0.8, transform=ax.transAxes, zorder=3,
    )
    ax.add_patch(badge)
    ax.text(0.895, 0.865, rec.impact, transform=ax.transAxes,
            fontsize=6.5, color=ic, fontweight="bold", ha="center", va="center", zorder=4)

    # index number (large, watermark style)
    ax.text(0.04, 0.88, str(index), transform=ax.transAxes,
            fontsize=20, fontweight="bold", color=ic + "40", va="top", zorder=2)

    # title
    ax.text(0.12, 0.90, rec.title, transform=ax.transAxes,
            fontsize=8.5, fontweight="bold", color=C["text"], va="top", zorder=3)

    # body (AI narrative or specifics)
    body = rec.narrative if rec.narrative else rec.specifics
    ax.text(0.04, 0.64, textwrap.fill(body, width=68),
            transform=ax.transAxes,
            fontsize=7.5, color=C["body"], va="top", linespacing=1.35, zorder=3)

    # action
    ax.text(0.04, 0.28, textwrap.fill(f"→  {rec.action}", width=70),
            transform=ax.transAxes,
            fontsize=7.5, color=C["primary"], fontweight="bold",
            va="top", linespacing=1.30, zorder=3)

    # savings
    if rec.monthly_impact > 0:
        ax.text(0.96, 0.08, f"~{fmt(rec.monthly_impact)}/mo",
                transform=ax.transAxes,
                fontsize=8, color=C["success"], fontweight="bold",
                ha="right", va="bottom", zorder=3)


def _page_recommendations(df, pdf, result: RecommendationResult, page_num: int) -> None:
    apply_style()
    fig = new_figure()
    month_label = df["Date"].dt.strftime("%B %Y").mode()[0]
    page_header_band(fig, "Recommendations — Action Plan",
                     f"Data-driven improvements for {month_label}")
    page_footer(fig, page_num)

    recs = result.recommendations
    if not recs:
        ax = fig.add_axes([0.1, 0.4, 0.8, 0.2])
        ax.axis("off")
        ax.text(0.5, 0.5, "No specific recommendations — spending looks healthy!",
                ha="center", va="center", fontsize=12, color=C["success"])
        pdf.savefig(fig, bbox_inches="tight"); plt.close(fig)
        return

    n = min(len(recs), 6)
    cols = 2
    card_w = 0.47
    card_h = 0.76 / ((n + 1) // cols) - 0.018
    x_starts = [0.02, 0.51]
    y_top = 0.885

    for i, rec in enumerate(recs[:n]):
        col = i % cols
        row = i // cols
        y = y_top - row * (card_h + 0.022) - card_h
        _rec_card(fig, x_starts[col], y, card_w, card_h, rec, i + 1)

    total_saving = sum(r.monthly_impact for r in recs if r.monthly_impact > 0)
    if total_saving > 0:
        ax_strip = fig.add_axes([0.02, 0.01, 0.96, 0.042])
        ax_strip.axis("off"); ax_strip.set_xlim(0, 1); ax_strip.set_ylim(0, 1)
        strip_bg = FancyBboxPatch(
            (0, 0), 1, 1, boxstyle="round,pad=0.02",
            facecolor=C["success"] + "22", edgecolor=C["success"] + "66",
            linewidth=1, transform=ax_strip.transAxes,
        )
        ax_strip.add_patch(strip_bg)
        ax_strip.text(
            0.5, 0.5,
            f"Implementing these recommendations could free up  ~{fmt(total_saving)}/month  "
            f"=  {fmt(total_saving * 12)}/year",
            ha="center", va="center", transform=ax_strip.transAxes,
            fontsize=9.5, color=C["success"], fontweight="bold",
        )

    pdf.savefig(fig, bbox_inches="tight")
    plt.close(fig)


# ── PAGE 12: Gaps + Budget ─────────────────────────────────────────────────────

def _page_budget(df, pdf, result: RecommendationResult, page_num: int) -> None:
    apply_style()
    fig = new_figure()
    month_label = df["Date"].dt.strftime("%B %Y").mode()[0]
    page_header_band(fig, "Gaps & Next-Month Budget Targets", month_label)
    page_footer(fig, page_num)

    # ── missing categories ────────────────────────────────────────────────────
    ax_miss_title = fig.add_axes([0.03, 0.865, 0.44, 0.04])
    ax_miss_title.axis("off")
    ax_miss_title.text(0, 0.5, "WHAT'S MISSING FROM YOUR SPENDING",
                       fontsize=10, fontweight="bold", color=C["danger"], va="center")

    for i, m in enumerate(result.missing[:4]):
        y_card = 0.845 - i * 0.195
        ax = fig.add_axes([0.03, y_card - 0.155, 0.44, 0.155])
        ax.axis("off"); ax.set_xlim(0, 1); ax.set_ylim(0, 1)

        card_bg = FancyBboxPatch(
            (0, 0), 1, 1, boxstyle="round,pad=0.03",
            facecolor="#FFF5F5", edgecolor=C["danger"] + "44",
            linewidth=0.8, transform=ax.transAxes, zorder=1,
        )
        ax.add_patch(card_bg)
        accent = FancyBboxPatch(
            (0, 0), 0.022, 1, boxstyle="round,pad=0.01",
            facecolor=C["danger"], edgecolor="none",
            transform=ax.transAxes, zorder=2,
        )
        ax.add_patch(accent)

        ax.text(0.05, 0.85, m.name, transform=ax.transAxes,
                fontsize=9, fontweight="bold", color=C["danger"], va="top", zorder=3)
        ax.text(0.05, 0.55, textwrap.fill(m.why, width=52),
                transform=ax.transAxes,
                fontsize=7.5, color=C["body"], va="top", linespacing=1.3, zorder=3)
        ax.text(0.05, 0.12, f"Suggested: {m.suggested_amount}",
                transform=ax.transAxes,
                fontsize=8, color=C["success"], fontweight="bold", va="top", zorder=3)

    # ── budget table ──────────────────────────────────────────────────────────
    ax_bud_title = fig.add_axes([0.52, 0.865, 0.45, 0.04])
    ax_bud_title.axis("off")
    ax_bud_title.text(0, 0.5, "SUGGESTED BUDGET — NEXT MONTH",
                      fontsize=10, fontweight="bold", color=C["primary"], va="center")

    if result.budget_targets:
        ax_b = fig.add_axes([0.52, 0.09, 0.45, 0.77])
        ax_b.axis("off")
        headers = ["Category", "This Month", "Target", "Change"]
        rows_data = [
            [t.category, t.current, t.suggested, f"{t.change_pct:+.0f}%"]
            for t in result.budget_targets[:7]
        ]
        table = ax_b.table(
            cellText=rows_data,
            colLabels=headers,
            cellLoc="center",
            loc="upper center",
            bbox=[0, 0, 1, 1],
        )
        table.auto_set_font_size(False)
        table.set_fontsize(9.5)
        col_widths = [0.38, 0.20, 0.22, 0.20]
        for (r, cc), cell in table.get_celld().items():
            cell.set_edgecolor(C["border"])
            cell.set_linewidth(0.5)
            if cc < len(col_widths):
                cell.set_width(col_widths[cc])
            if r == 0:
                cell.set_facecolor(C["header_bg"])
                cell.set_text_props(color="white", fontweight="bold")
            elif r % 2 == 0:
                cell.set_facecolor("#EEF2FF")
            else:
                cell.set_facecolor(C["card"])
            if cc == 3 and r > 0:
                txt = rows_data[r - 1][3] if r - 1 < len(rows_data) else ""
                if txt.startswith("-"):
                    cell.set_text_props(color=C["success"], fontweight="bold")
                elif txt.startswith("+"):
                    cell.set_text_props(color=C["danger"], fontweight="bold")

    pdf.savefig(fig, bbox_inches="tight")
    plt.close(fig)


# ── public entry point ─────────────────────────────────────────────────────────

def render(
    df: pd.DataFrame, pdf,
    score: ScoreResult,
    result: RecommendationResult,
    ai_data: dict | None = None,
    start_page: int = 10,
) -> None:
    ai_verdict = (ai_data or {}).get("score_verdict", "")
    _page_score(df, pdf, score, result, ai_verdict, start_page)
    _page_recommendations(df, pdf, result, start_page + 1)
    _page_budget(df, pdf, result, start_page + 2)
