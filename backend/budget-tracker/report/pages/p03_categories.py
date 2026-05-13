import matplotlib.pyplot as plt
import pandas as pd

from ..theme import (
    C, CAT_COLORS, apply_style, new_figure, page_header_band,
    page_footer, fmt, rs_formatter, add_chart_frame,
)


def render(df: pd.DataFrame, pdf, page_num: int = 4) -> None:
    apply_style()
    fig = new_figure()
    month_label = df["Date"].dt.strftime("%B %Y").mode()[0]
    page_header_band(fig, "Category Breakdown", month_label)
    page_footer(fig, page_num)

    d = df[df["Type"] == "Debit"]
    cat = d.groupby("Category")["Amount"].sum().sort_values(ascending=False)
    total = cat.sum()

    # ── donut chart ───────────────────────────────────────────────────────────
    ax1 = fig.add_axes([0.01, 0.07, 0.40, 0.80])
    ax1.axis("off")
    ax1.set_facecolor("none")

    wedges, _, autotexts = ax1.pie(
        cat.values,
        labels=None,
        autopct=lambda p: f"{p:.1f}%" if p > 4 else "",
        colors=CAT_COLORS[:len(cat)],
        startangle=90,
        pctdistance=0.80,
        wedgeprops={"linewidth": 2.5, "edgecolor": C["bg"]},
    )
    for at in autotexts:
        at.set_fontsize(7.5); at.set_fontweight("bold")

    centre = plt.Circle((0, 0), 0.52, color=C["card"], zorder=10)
    ax1.add_patch(centre)
    ax1.text(0, 0.10, fmt(total), ha="center", va="center",
             fontsize=13, fontweight="bold", color=C["text"])
    ax1.text(0, -0.18, "Total Spent", ha="center", va="center",
             fontsize=8, color=C["muted"])
    ax1.set_title("Category Split", fontweight="bold", pad=8, fontsize=10)

    legend_labels = [
        f"{c}  ({fmt(v)}, {v / total * 100:.1f}%)"
        for c, v in zip(cat.index, cat.values)
    ]
    ax1.legend(wedges, legend_labels, loc="lower center",
               bbox_to_anchor=(0.5, -0.24), ncol=2, fontsize=7,
               frameon=True, edgecolor=C["border"])

    # ── sub-category bars for top 3 ───────────────────────────────────────────
    top3 = cat.head(3).index.tolist()
    positions = [(0.44, 0.65), (0.44, 0.39), (0.44, 0.12)]

    for idx, (cat_name, (x, y)) in enumerate(zip(top3, positions)):
        sub = (
            d[d["Category"] == cat_name]
            .groupby("Subcategory")["Amount"].sum()
            .sort_values(ascending=True).tail(5)
        )
        ax = fig.add_axes([x, y, 0.54, 0.20])
        color = CAT_COLORS[list(cat.index).index(cat_name)]
        add_chart_frame(ax, f"{cat_name}  ·  {fmt(cat[cat_name])}", color=color)

        bars = ax.barh(sub.index, sub.values, color=color, height=0.52,
                       alpha=0.85, zorder=3)
        ax.xaxis.set_major_formatter(rs_formatter())
        ax.grid(axis="x", alpha=0.30, zorder=0); ax.set_axisbelow(True)
        for bar, val in zip(bars, sub.values):
            ax.text(val + sub.max() * 0.025,
                    bar.get_y() + bar.get_height() / 2,
                    fmt(val), va="center", fontsize=7)

    pdf.savefig(fig, bbox_inches="tight")
    plt.close(fig)
