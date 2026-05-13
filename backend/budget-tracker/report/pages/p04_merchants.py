import textwrap
import matplotlib.pyplot as plt
import pandas as pd

from ..theme import (
    C, CAT_COLORS, apply_style, new_figure, page_header_band,
    page_footer, fmt, rs_formatter, add_chart_frame,
)


def render(df: pd.DataFrame, pdf, page_num: int = 5) -> None:
    apply_style()
    fig = new_figure()
    month_label = df["Date"].dt.strftime("%B %Y").mode()[0]
    page_header_band(fig, "Top Merchants & Transaction Profile", month_label)
    page_footer(fig, page_num)

    d = df[df["Type"] == "Debit"]

    # ── top merchants by spend ────────────────────────────────────────────────
    ax1 = fig.add_axes([0.04, 0.55, 0.55, 0.35])
    add_chart_frame(ax1, "Top Merchants by Total Spend")
    top_m = d.groupby("Description")["Amount"].sum().sort_values(ascending=True).tail(12)
    colors_m = [CAT_COLORS[i % len(CAT_COLORS)] for i in range(len(top_m))]
    bars = ax1.barh(
        [textwrap.shorten(m, 30) for m in top_m.index],
        top_m.values, color=colors_m, height=0.62, zorder=3,
    )
    ax1.xaxis.set_major_formatter(rs_formatter())
    ax1.margins(x=0.20)
    ax1.grid(axis="x", alpha=0.35, zorder=0); ax1.set_axisbelow(True)
    for bar, val in zip(bars, top_m.values):
        ax1.text(val + top_m.max() * 0.012,
                 bar.get_y() + bar.get_height() / 2,
                 fmt(val), va="center", fontsize=7.5, color=C["body"])

    # ── top by frequency ──────────────────────────────────────────────────────
    ax2 = fig.add_axes([0.65, 0.55, 0.31, 0.35])
    add_chart_frame(ax2, "Most Frequent Merchants")
    top_freq = d["Description"].value_counts().head(8)
    ax2.barh(
        [textwrap.shorten(m, 22) for m in top_freq.index],
        top_freq.values, color=C["secondary"], height=0.62, zorder=3,
    )
    ax2.set_xlabel("No. of Transactions")
    ax2.grid(axis="x", alpha=0.35, zorder=0); ax2.set_axisbelow(True)
    for i, val in enumerate(top_freq.values):
        ax2.text(val + 0.1, i, str(val), va="center", fontsize=7.5, color=C["body"])

    # ── transaction size distribution ─────────────────────────────────────────
    ax3 = fig.add_axes([0.04, 0.09, 0.44, 0.36])
    add_chart_frame(ax3, "Transaction Size Distribution")
    bucket_order = [
        "Rs.0-50 (Micro)", "Rs.51-200 (Small)", "Rs.201-500 (Medium)",
        "Rs.501-1000 (Large)", "Rs.1001-5000 (Major)", "Rs.5000+ (Mega)",
    ]
    bucket_counts = d["Amount_Bucket"].value_counts().reindex(bucket_order, fill_value=0)
    bucket_colors = [
        C["success"], C["primary"], C["accent"],
        C["secondary"], C["danger"], "#7C3AED",
    ]
    bars3 = ax3.bar(range(len(bucket_counts)), bucket_counts.values,
                    color=bucket_colors, width=0.62, zorder=3)
    ax3.set_xticks(range(len(bucket_counts)))
    ax3.set_xticklabels(
        [b.split(" ")[0] for b in bucket_counts.index], rotation=30, ha="right", fontsize=7,
    )
    ax3.set_ylabel("No. of Transactions")
    ax3.grid(axis="y", alpha=0.35, zorder=0); ax3.set_axisbelow(True)
    for bar, val in zip(bars3, bucket_counts.values):
        ax3.text(bar.get_x() + bar.get_width() / 2, val + 0.25,
                 str(val), ha="center", fontsize=8, color=C["body"])

    # ── recurring vs one-time donut ────────────────────────────────────────────
    ax4 = fig.add_axes([0.57, 0.09, 0.38, 0.36])
    ax4.axis("off")
    add_chart_frame(ax4, "Recurring vs One-time Spend")
    rec = d.groupby("Is_Recurring")["Amount"].agg(["sum", "count"])
    vals_r = [
        rec.loc["No",  "sum"] if "No"  in rec.index else 0,
        rec.loc["Yes", "sum"] if "Yes" in rec.index else 0,
    ]
    wedges, _, ats = ax4.pie(
        vals_r, labels=["One-time", "Recurring"], autopct="%1.1f%%",
        colors=[C["primary"], C["accent"]],
        wedgeprops={"linewidth": 2.5, "edgecolor": C["bg"]},
        startangle=90,
    )
    for at in ats:
        at.set_fontsize(8); at.set_fontweight("bold")

    pdf.savefig(fig, bbox_inches="tight")
    plt.close(fig)
