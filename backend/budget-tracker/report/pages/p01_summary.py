import matplotlib.gridspec as gridspec
import matplotlib.pyplot as plt
import pandas as pd

from ..theme import (
    C, CAT_COLORS, apply_style, new_figure, page_header_band,
    page_footer, stat_card, fmt, rs_formatter, add_chart_frame, gradient_fill,
)


def render(df: pd.DataFrame, pdf, page_num: int = 2) -> None:
    apply_style()
    fig = new_figure()
    month_label = df["Date"].dt.strftime("%B %Y").mode()[0]
    page_header_band(fig, "Executive Summary", month_label)
    page_footer(fig, page_num)

    d = df[df["Type"] == "Debit"]
    c = df[df["Type"] == "Credit"]
    total_spent    = d["Amount"].sum()
    total_received = c["Amount"].sum()
    net            = total_spent - total_received
    n_txns         = len(df)
    avg_daily      = total_spent / max(df["Date"].nunique(), 1)
    biggest        = d.nlargest(1, "Amount").iloc[0] if len(d) else None
    n_sources      = df["Source"].nunique()

    # ── KPI stat cards (2 rows × 4 cols) ─────────────────────────────────────
    gs = gridspec.GridSpec(2, 4, figure=fig,
                           top=0.87, bottom=0.55, hspace=0.30, wspace=0.18,
                           left=0.04, right=0.96)
    stats = [
        ("Total Spent",            fmt(total_spent),    C["danger"]),
        ("Total Received",         fmt(total_received), C["success"]),
        ("Net Outflow",            fmt(net),            C["primary"]),
        ("Transactions",           str(n_txns),         C["secondary"]),
        ("Avg Daily Spend",        fmt(avg_daily),      C["accent"]),
        ("Biggest Transaction",    fmt(biggest["Amount"]) if biggest is not None else "—", "#0891B2"),
        ("Payment Sources",        str(n_sources),      "#059669"),
        ("Days with Spending",     str(df["Date"].nunique()), "#7C3AED"),
    ]
    for i, (lbl, val, col) in enumerate(stats):
        ax = fig.add_subplot(gs[i // 4, i % 4])
        stat_card(ax, lbl, val, col)

    # ── category bar chart ────────────────────────────────────────────────────
    ax2 = fig.add_axes([0.04, 0.08, 0.54, 0.40])
    add_chart_frame(ax2, "Top Spending Categories")

    cat = d.groupby("Category")["Amount"].sum().sort_values(ascending=True).tail(10)
    bars = ax2.barh(cat.index, cat.values,
                    color=CAT_COLORS[:len(cat)], height=0.62, zorder=3)
    ax2.set_xlabel("Amount (Rs.)")
    ax2.xaxis.set_major_formatter(rs_formatter())
    ax2.grid(axis="x", alpha=0.35, zorder=0)
    ax2.set_axisbelow(True)
    for bar, val in zip(bars, cat.values):
        ax2.text(val + total_spent * 0.004, bar.get_y() + bar.get_height() / 2,
                 fmt(val), va="center", fontsize=7.5, color=C["body"])

    # ── payment source donut ──────────────────────────────────────────────────
    ax3 = fig.add_axes([0.63, 0.08, 0.33, 0.40])
    add_chart_frame(ax3, "Spent by Source")
    ax3.axis("off")

    src = d.groupby("Source")["Amount"].sum()
    wedges, _, autotexts = ax3.pie(
        src.values, labels=None, autopct="%1.1f%%",
        colors=CAT_COLORS[:len(src)], startangle=90,
        wedgeprops={"linewidth": 2.5, "edgecolor": C["bg"]},
        pctdistance=0.78,
    )
    for at in autotexts:
        at.set_fontsize(8); at.set_color("white"); at.set_fontweight("bold")

    import matplotlib.pyplot as mpl_plt
    centre = mpl_plt.Circle((0, 0), 0.50, color=C["card"], zorder=10)
    ax3.add_patch(centre)
    ax3.text(0, 0.07, fmt(total_spent), ha="center", va="center",
             fontsize=11, fontweight="bold", color=C["text"])
    ax3.text(0, -0.18, "total", ha="center", va="center",
             fontsize=8, color=C["muted"])
    ax3.legend(src.index, loc="lower center",
               bbox_to_anchor=(0.5, -0.22), ncol=1, fontsize=7.5)

    pdf.savefig(fig, bbox_inches="tight")
    plt.close(fig)
