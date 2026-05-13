import numpy as np
import matplotlib.pyplot as plt
import pandas as pd

from ..theme import (
    C, CAT_COLORS, apply_style, new_figure, page_header_band,
    page_footer, fmt, rs_formatter, add_chart_frame, gradient_fill,
)


def render(df: pd.DataFrame, pdf, page_num: int = 8) -> None:
    apply_style()
    fig = new_figure()
    month_label = df["Date"].dt.strftime("%B %Y").mode()[0]
    page_header_band(fig, "Advanced Analytics", month_label)
    page_footer(fig, page_num)

    d = df[df["Type"] == "Debit"]
    total_spent = d["Amount"].sum()

    # ── cumulative spend curve ────────────────────────────────────────────────
    ax1 = fig.add_axes([0.05, 0.55, 0.55, 0.34])
    add_chart_frame(ax1, "Cumulative Spending Curve")

    daily = d.groupby("Date")["Amount"].sum().reindex(
        pd.date_range(d["Date"].min(), d["Date"].max()), fill_value=0
    )
    cumsum = daily.cumsum()
    days   = np.arange(1, len(cumsum) + 1)
    ideal  = np.linspace(0, total_spent, len(days))

    gradient_fill(ax1, days, cumsum.values, C["primary"], alpha_top=0.25, alpha_bot=0.02)
    ax1.plot(days, cumsum.values, color=C["primary"],  linewidth=2.2, label="Actual",    zorder=5)
    ax1.plot(days, ideal,         color=C["muted"],    linewidth=1.5, linestyle="--",
             label="Even pace", zorder=4)
    ax1.fill_between(days,
                     np.where(cumsum.values > ideal, cumsum.values, ideal), ideal,
                     alpha=0.22, color=C["danger"], label="Ahead of pace", zorder=3)

    ax1.set_xlabel("Day of Month")
    ax1.set_ylabel("Cumulative (Rs.)")
    ax1.yaxis.set_major_formatter(rs_formatter())
    ax1.legend(fontsize=7.5, frameon=True)
    ax1.grid(alpha=0.25, zorder=0); ax1.set_axisbelow(True)

    # ── spending heatmap ──────────────────────────────────────────────────────
    ax2 = fig.add_axes([0.65, 0.55, 0.31, 0.34])
    add_chart_frame(ax2, "Heatmap  ·  Week × Day")

    d2 = d.copy()
    d2["week_num"] = d2["Date"].dt.isocalendar().week
    d2["dow"]      = d2["Date"].dt.dayofweek
    pivot = d2.pivot_table(values="Amount", index="week_num", columns="dow",
                           aggfunc="sum", fill_value=0)
    pivot.columns = ["M", "T", "W", "Th", "F", "Sa", "Su"]

    im = ax2.imshow(pivot.values, aspect="auto", cmap="Blues", interpolation="nearest")
    ax2.set_xticks(range(len(pivot.columns)))
    ax2.set_xticklabels(pivot.columns, fontsize=7.5)
    ax2.set_yticks(range(len(pivot.index)))
    ax2.set_yticklabels([f"W{w}" for w in pivot.index], fontsize=7.5)
    for i in range(pivot.shape[0]):
        for j in range(pivot.shape[1]):
            v = pivot.values[i, j]
            if v > 0:
                ax2.text(j, i, fmt(v), ha="center", va="center", fontsize=5.5,
                         color="white" if v > pivot.values.max() * 0.55 else C["body"])
    plt.colorbar(im, ax=ax2, fraction=0.046, pad=0.04).ax.tick_params(labelsize=6)

    # ── week-over-week stacked bar (top 5 cats) ────────────────────────────────
    ax3 = fig.add_axes([0.05, 0.09, 0.55, 0.36])
    add_chart_frame(ax3, "Top 5 Categories — Week by Week")

    top5 = d.groupby("Category")["Amount"].sum().nlargest(5).index.tolist()
    weekly_cat = (
        d[d["Category"].isin(top5)]
        .groupby(["Week_Label", "Category"])["Amount"].sum()
        .unstack(fill_value=0)
        .reindex(columns=top5, fill_value=0)
    )
    x_pos  = range(len(weekly_cat))
    bottom = np.zeros(len(weekly_cat))
    for i, cat in enumerate(top5):
        vals = weekly_cat[cat].values if cat in weekly_cat.columns else np.zeros(len(weekly_cat))
        ax3.bar(x_pos, vals, bottom=bottom, label=cat,
                color=CAT_COLORS[i], width=0.65, alpha=0.90, zorder=3)
        bottom += vals
    ax3.set_xticks(list(x_pos))
    ax3.set_xticklabels([w.replace(" - ", "\n") for w in weekly_cat.index], fontsize=7)
    ax3.set_ylabel("Amount (Rs.)")
    ax3.yaxis.set_major_formatter(rs_formatter())
    ax3.legend(fontsize=7, loc="upper right", frameon=True)
    ax3.grid(axis="y", alpha=0.30, zorder=0); ax3.set_axisbelow(True)

    # ── avg transaction by category ───────────────────────────────────────────
    ax4 = fig.add_axes([0.65, 0.09, 0.31, 0.36])
    add_chart_frame(ax4, "Avg Transaction\nby Category")

    avg_txn = d.groupby("Category").agg(total=("Amount", "sum"), count=("Amount", "count"))
    avg_txn["avg"] = avg_txn["total"] / avg_txn["count"]
    avg_txn = avg_txn.sort_values("avg", ascending=True).tail(8)
    colors_a = [CAT_COLORS[i % len(CAT_COLORS)] for i in range(len(avg_txn))]
    ax4.barh(avg_txn.index, avg_txn["avg"].values, color=colors_a, height=0.55, zorder=3)
    ax4.xaxis.set_major_formatter(rs_formatter())
    ax4.grid(axis="x", alpha=0.30, zorder=0); ax4.set_axisbelow(True)
    for i, val in enumerate(avg_txn["avg"].values):
        ax4.text(val + avg_txn["avg"].max() * 0.012, i, fmt(val),
                 va="center", fontsize=7.5, color=C["body"])

    pdf.savefig(fig, bbox_inches="tight")
    plt.close(fig)
