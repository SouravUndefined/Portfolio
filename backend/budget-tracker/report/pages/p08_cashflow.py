import numpy as np
import matplotlib.pyplot as plt
import pandas as pd

from ..theme import (
    C, CAT_COLORS, apply_style, new_figure, page_header_band,
    page_footer, fmt, rs_formatter, add_chart_frame,
)


def render(df: pd.DataFrame, pdf, page_num: int = 9) -> None:
    apply_style()
    fig = new_figure()
    month_label = df["Date"].dt.strftime("%B %Y").mode()[0]
    page_header_band(fig, "Cash Flow & Transaction Profile", month_label)
    page_footer(fig, page_num)

    d = df[df["Type"] == "Debit"]
    c = df[df["Type"] == "Credit"]

    # ── daily inflow vs outflow bar chart ─────────────────────────────────────
    ax1 = fig.add_axes([0.05, 0.55, 0.90, 0.34])
    add_chart_frame(ax1, "Daily Cash Flow — Inflow vs Outflow")

    date_range = pd.date_range(df["Date"].min(), df["Date"].max())
    daily_out  = d.groupby("Date")["Amount"].sum().reindex(date_range, fill_value=0)
    daily_in   = c.groupby("Date")["Amount"].sum().reindex(date_range, fill_value=0)
    net_daily  = daily_in - daily_out
    x = np.arange(len(date_range))

    ax1.bar(x, -daily_out.values, color=C["danger"],  alpha=0.72, label="Outflow", width=0.6, zorder=3)
    ax1.bar(x,  daily_in.values,  color=C["success"], alpha=0.72, label="Inflow",  width=0.6, zorder=3)
    ax1.plot(x, net_daily.values, color=C["primary"], linewidth=2.2, label="Net", zorder=5)
    ax1.axhline(0, color=C["muted"], linewidth=0.8, linestyle="--", zorder=4)
    ax1.set_xticks(x[::2])
    ax1.set_xticklabels(
        [dt.strftime("%d %b") for dt in date_range[::2]], rotation=40, ha="right", fontsize=7
    )
    ax1.yaxis.set_major_formatter(rs_formatter())
    ax1.legend(fontsize=8, frameon=True)
    ax1.grid(axis="y", alpha=0.25, zorder=0); ax1.set_axisbelow(True)

    # ── transaction count by category ─────────────────────────────────────────
    ax2 = fig.add_axes([0.05, 0.09, 0.27, 0.36])
    add_chart_frame(ax2, "Transaction Count\nby Category")
    cnt = d.groupby("Category")["Amount"].count().sort_values(ascending=True).tail(8)
    ax2.barh(cnt.index, cnt.values, color=C["primary"], height=0.55, alpha=0.90, zorder=3)
    ax2.set_xlabel("No. of Transactions")
    ax2.grid(axis="x", alpha=0.30, zorder=0); ax2.set_axisbelow(True)
    for i, v in enumerate(cnt.values):
        ax2.text(v + 0.1, i, str(v), va="center", fontsize=8, color=C["body"])

    # ── first half vs second half ──────────────────────────────────────────────
    ax3 = fig.add_axes([0.38, 0.09, 0.27, 0.36])
    add_chart_frame(ax3, "First Half vs\nSecond Half")
    mid    = df["Date"].min() + (df["Date"].max() - df["Date"].min()) / 2
    first  = d[d["Date"] <= mid]["Amount"].sum()
    second = d[d["Date"] >  mid]["Amount"].sum()
    bars   = ax3.bar(["First Half", "Second Half"], [first, second],
                     color=[C["primary"], C["secondary"]], width=0.52, zorder=3)
    ax3.yaxis.set_major_formatter(rs_formatter())
    ax3.grid(axis="y", alpha=0.30, zorder=0); ax3.set_axisbelow(True)
    for bar, val in zip(bars, [first, second]):
        ax3.text(bar.get_x() + bar.get_width() / 2,
                 val + max(first, second) * 0.012,
                 fmt(val), ha="center", fontsize=9, fontweight="bold", color=C["body"])
    pct = first / (first + second) * 100 if (first + second) > 0 else 50
    ax3.text(0.5, 0.06, f"{pct:.0f}% in first half",
             ha="center", transform=ax3.transAxes, fontsize=8, color=C["muted"])

    # ── top transactions table ────────────────────────────────────────────────
    ax4 = fig.add_axes([0.70, 0.09, 0.27, 0.36])
    ax4.axis("off")
    add_chart_frame(ax4, "Top Transactions")

    top10 = d.nlargest(8, "Amount")[["Date", "Description", "Amount"]].copy()
    top10["Date"]        = pd.to_datetime(top10["Date"]).dt.strftime("%d %b")
    top10["Description"] = top10["Description"].str[:20]
    top10["Amount"]      = top10["Amount"].apply(lambda x: f"Rs.{x:,.0f}")

    table = ax4.table(
        cellText=top10.values,
        colLabels=["Date", "Description", "Amount"],
        cellLoc="left", loc="upper left",
        bbox=[0, 0, 1, 1],
    )
    table.auto_set_font_size(False)
    table.set_fontsize(7.5)
    for (r, cc), cell in table.get_celld().items():
        cell.set_edgecolor(C["border"])
        if r == 0:
            cell.set_facecolor(C["header_bg"])
            cell.set_text_props(color="white", fontweight="bold")
        elif r % 2 == 0:
            cell.set_facecolor("#EEF2FF")
        else:
            cell.set_facecolor(C["card"])

    pdf.savefig(fig, bbox_inches="tight")
    plt.close(fig)
