import textwrap
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch
import pandas as pd

from ..theme import C, CAT_COLORS, apply_style, new_figure, page_header_band, page_footer, fmt


def render(df: pd.DataFrame, pdf, page_num: int = 7) -> None:
    apply_style()
    fig = new_figure()
    month_label = df["Date"].dt.strftime("%B %Y").mode()[0]
    page_header_band(fig, "Key Insights & Highlights", month_label)
    page_footer(fig, page_num)

    d = df[df["Type"] == "Debit"]
    c = df[df["Type"] == "Credit"]
    total_spent = d["Amount"].sum()
    insights = []

    by_day = d.groupby("Date")["Amount"].sum()
    if len(by_day):
        max_day = by_day.idxmax()
        insights.append(("Biggest Spending Day",
            f"{max_day.strftime('%d %b %Y')} — {fmt(by_day.max())} spent "
            f"({by_day.max() / total_spent * 100:.1f}% of monthly total)"))

    top_cat = d.groupby("Category")["Amount"].sum().idxmax()
    top_cat_amt = d.groupby("Category")["Amount"].sum().max()
    insights.append(("Highest Spend Category",
        f"{top_cat} — {fmt(top_cat_amt)} ({top_cat_amt / total_spent * 100:.1f}% of total)"))

    d2 = d.copy(); d2["is_wknd"] = d2["Is_Weekend"] == "Yes"
    wknd_avg = d2[d2.is_wknd]["Amount"].mean() if d2[d2.is_wknd].shape[0] else 0
    wkdy_avg = d2[~d2.is_wknd]["Amount"].mean() if d2[~d2.is_wknd].shape[0] else 0
    if wknd_avg and wkdy_avg:
        ratio = wknd_avg / wkdy_avg
        txt = (
            f"Weekend avg Rs.{wknd_avg:,.0f} vs weekday Rs.{wkdy_avg:,.0f} — "
            + (f"weekends cost {(ratio-1)*100:.0f}% more per transaction"
               if ratio > 1
               else f"weekdays cost {(1/ratio-1)*100:.0f}% more")
        )
        insights.append(("Weekend vs Weekday", txt))

    rec_total = d[d["Is_Recurring"] == "Yes"]["Amount"].sum()
    rec_count = d[d["Is_Recurring"] == "Yes"]["Description"].nunique()
    if rec_total > 0:
        insights.append(("Recurring Subscriptions",
            f"Rs.{rec_total:,.2f} across {rec_count} recurring services "
            f"({rec_total / total_spent * 100:.1f}% of total spend)"))

    if len(d):
        big = d.nlargest(1, "Amount").iloc[0]
        insights.append(("Largest Single Transaction",
            f"{fmt(big['Amount'])} — {big['Description']} on "
            f"{pd.Timestamp(big['Date']).strftime('%d %b')}"))

    top_src = d.groupby("Source")["Amount"].sum().idxmax()
    top_src_pct = d.groupby("Source")["Amount"].sum().max() / total_spent * 100
    insights.append(("Primary Payment Source",
        f"{top_src} — {top_src_pct:.1f}% of total spend"))

    if len(c) and c["Amount"].sum() > 0:
        insights.append(("Cashback & Credits Received",
            f"Rs.{c['Amount'].sum():,.2f} received ({len(c)} credit transactions)  —  "
            f"effective net spend: {fmt(total_spent - c['Amount'].sum())}"))

    all_days = pd.date_range(d["Date"].min(), d["Date"].max())
    zero_days = len(all_days) - d["Date"].dt.normalize().nunique()
    insights.append(("Days Without Spending",
        f"{zero_days} days out of {len(all_days)} had no recorded spend"))

    micro = d[d["Amount"] <= 50]
    if len(micro):
        insights.append(("Micro Transactions (≤ Rs.50)",
            f"{len(micro)} transactions totalling Rs.{micro['Amount'].sum():,.2f}"))

    dow_total = d.groupby("Day_Name")["Amount"].sum()
    if len(dow_total):
        top_dow = dow_total.idxmax()
        insights.append(("Most Expensive Day of Week",
            f"{top_dow} — {fmt(dow_total.max())} total this month"))

    n = len(insights)
    cols = 2
    rows = (n + 1) // cols

    ax_bg = fig.add_axes([0, 0, 1, 0.93])
    ax_bg.axis("off")
    ax_bg.set_facecolor(C["bg"])

    for idx, (title, body) in enumerate(insights):
        col = idx % cols
        row = idx // cols
        pad_l  = 0.03
        gap    = 0.025
        cell_w = (1 - pad_l * 2 - gap) / cols
        cell_h = 0.84 / rows - 0.010
        x = pad_l + col * (cell_w + gap)
        y = 0.88 - (row + 1) * (cell_h + 0.010)

        ax = fig.add_axes([x, y, cell_w, cell_h])
        ax.axis("off")
        ax.set_xlim(0, 1); ax.set_ylim(0, 1)

        bar_color = CAT_COLORS[idx % len(CAT_COLORS)]

        # card background
        card = FancyBboxPatch(
            (0.0, 0.0), 1.0, 1.0,
            boxstyle="round,pad=0.02",
            facecolor=C["card"], edgecolor=C["border"],
            linewidth=0.8, transform=ax.transAxes, zorder=1,
        )
        ax.add_patch(card)

        # coloured left accent bar
        accent = FancyBboxPatch(
            (0.0, 0.0), 0.025, 1.0,
            boxstyle="round,pad=0.01",
            facecolor=bar_color, edgecolor="none",
            transform=ax.transAxes, zorder=2,
        )
        ax.add_patch(accent)

        ax.text(0.05, 0.74, title, transform=ax.transAxes,
                fontsize=9, fontweight="bold", color=bar_color, va="top")
        wrapped = textwrap.fill(body, width=74)
        ax.text(0.05, 0.44, wrapped, transform=ax.transAxes,
                fontsize=8, color=C["body"], va="top", linespacing=1.40)

    pdf.savefig(fig, bbox_inches="tight")
    plt.close(fig)
