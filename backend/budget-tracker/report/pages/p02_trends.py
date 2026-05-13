import matplotlib.pyplot as plt
import pandas as pd

from ..theme import (
    C, CAT_COLORS, apply_style, new_figure, page_header_band,
    page_footer, fmt, rs_formatter, add_chart_frame, gradient_fill,
)


def render(df: pd.DataFrame, pdf, page_num: int = 3) -> None:
    apply_style()
    fig = new_figure()
    month_label = df["Date"].dt.strftime("%B %Y").mode()[0]
    page_header_band(fig, "Spending Trends", month_label)
    page_footer(fig, page_num)

    d = df[df["Type"] == "Debit"]

    daily = d.groupby("Date")["Amount"].sum().reindex(
        pd.date_range(d["Date"].min(), d["Date"].max()), fill_value=0
    )

    # ── daily area chart ──────────────────────────────────────────────────────
    ax1 = fig.add_axes([0.05, 0.56, 0.90, 0.33])
    add_chart_frame(ax1, "Daily Spending")

    gradient_fill(ax1, daily.index, daily.values, C["primary"],
                  alpha_top=0.35, alpha_bot=0.02)
    ax1.plot(daily.index, daily.values, color=C["primary"], linewidth=2.2, zorder=5)

    roll = daily.rolling(3, min_periods=1).mean()
    ax1.plot(roll.index, roll.values, color=C["danger"], linewidth=1.6,
             linestyle="--", label="3-day avg", zorder=6)

    ax1.set_ylabel("Amount (Rs.)")
    ax1.yaxis.set_major_formatter(rs_formatter())
    tick_dates = daily.index[::3]
    ax1.set_xticks(tick_dates)
    ax1.set_xticklabels([dt.strftime("%d %b") for dt in tick_dates],
                        rotation=40, ha="right", fontsize=7)
    ax1.grid(axis="y", alpha=0.35, zorder=0)
    ax1.set_axisbelow(True)
    ax1.legend(frameon=True)

    # ── day-of-week bar ───────────────────────────────────────────────────────
    ax2 = fig.add_axes([0.05, 0.09, 0.44, 0.36])
    add_chart_frame(ax2, "Spending by Day of Week")

    dow_order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    dow = d.groupby("Day_Name")["Amount"].sum().reindex(dow_order, fill_value=0)
    colors_dow = [C["accent"] if day in ("Saturday", "Sunday") else C["primary"]
                  for day in dow.index]
    bars = ax2.bar(range(len(dow)), dow.values, color=colors_dow, width=0.6, zorder=3)
    ax2.set_xticks(range(len(dow)))
    ax2.set_xticklabels([d[:3] for d in dow.index])
    ax2.set_ylabel("Amount (Rs.)")
    ax2.yaxis.set_major_formatter(rs_formatter())
    ax2.grid(axis="y", alpha=0.35, zorder=0); ax2.set_axisbelow(True)
    for bar, val in zip(bars, dow.values):
        if val > 0:
            ax2.text(bar.get_x() + bar.get_width() / 2, val + dow.max() * 0.012,
                     fmt(val), ha="center", fontsize=6.5, color=C["body"])

    # ── weekly bucket bars ─────────────────────────────────────────────────────
    ax3 = fig.add_axes([0.57, 0.09, 0.38, 0.36])
    add_chart_frame(ax3, "Spending by Week")

    weekly = d.groupby("Week_Label")["Amount"].sum()
    bar_colors = [CAT_COLORS[i % len(CAT_COLORS)] for i in range(len(weekly))]
    bars3 = ax3.bar(range(len(weekly)), weekly.values, color=bar_colors, width=0.55, zorder=3)
    ax3.set_xticks(range(len(weekly)))
    ax3.set_xticklabels([w.replace(" - ", "\n") for w in weekly.index], fontsize=7)
    ax3.set_ylabel("Amount (Rs.)")
    ax3.yaxis.set_major_formatter(rs_formatter())
    ax3.grid(axis="y", alpha=0.35, zorder=0); ax3.set_axisbelow(True)
    for i, val in enumerate(weekly.values):
        ax3.text(i, val + weekly.max() * 0.012, fmt(val),
                 ha="center", fontsize=7.5, color=C["body"])

    pdf.savefig(fig, bbox_inches="tight")
    plt.close(fig)
