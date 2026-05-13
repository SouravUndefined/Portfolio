import textwrap
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd

from ..theme import (
    C, CAT_COLORS, apply_style, new_figure, page_header_band,
    page_footer, fmt, rs_formatter, add_chart_frame,
)


def render(df: pd.DataFrame, pdf, page_num: int = 6) -> None:
    apply_style()
    fig = new_figure()
    month_label = df["Date"].dt.strftime("%B %Y").mode()[0]
    page_header_band(fig, "Essential vs Discretionary  ·  Payment Modes", month_label)
    page_footer(fig, page_num)

    d = df[df["Type"] == "Debit"]

    # ── stacked horizontal bar: essential vs discretionary ────────────────────
    ax1 = fig.add_axes([0.04, 0.55, 0.55, 0.35])
    add_chart_frame(ax1, "Essential vs Discretionary by Category")
    st = d.groupby(["Spend_Type", "Category"])["Amount"].sum().unstack(level=0, fill_value=0)
    cats = st.sum(axis=1).sort_values(ascending=True).index
    st = st.loc[cats]
    x = range(len(cats))
    bottom = np.zeros(len(cats))
    for col, color in zip(st.columns, [C["primary"], C["accent"]]):
        if col in st:
            ax1.barh(list(x), st[col].values, left=bottom, label=col,
                     color=color, height=0.55, alpha=0.88, zorder=3)
            bottom += st[col].values
    ax1.set_yticks(list(x))
    ax1.set_yticklabels([textwrap.shorten(c, 22) for c in cats], fontsize=7.5)
    ax1.xaxis.set_major_formatter(rs_formatter())
    ax1.legend(loc="lower right", frameon=True)
    ax1.grid(axis="x", alpha=0.30, zorder=0); ax1.set_axisbelow(True)

    # ── overall essential/discretionary donut ─────────────────────────────────
    ax2 = fig.add_axes([0.64, 0.55, 0.32, 0.35])
    ax2.axis("off")
    add_chart_frame(ax2, "Spend Type Split")
    ess = d.groupby("Spend_Type")["Amount"].sum()
    wedges, _, ats = ax2.pie(
        ess.values, labels=ess.index, autopct="%1.1f%%",
        colors=[C["primary"], C["accent"]],
        wedgeprops={"linewidth": 2.5, "edgecolor": C["bg"]},
        startangle=90,
    )
    for at in ats:
        at.set_fontsize(8.5); at.set_fontweight("bold")

    # ── payment mode bars ─────────────────────────────────────────────────────
    ax3 = fig.add_axes([0.04, 0.09, 0.44, 0.36])
    add_chart_frame(ax3, "Spending by Payment Mode")
    pm = d.groupby("Payment_Mode")["Amount"].sum().sort_values(ascending=True)
    pm_colors = [C["primary"], C["secondary"], C["success"], C["accent"]][:len(pm)]
    ax3.barh(pm.index, pm.values, color=pm_colors, height=0.55, zorder=3)
    ax3.xaxis.set_major_formatter(rs_formatter())
    ax3.grid(axis="x", alpha=0.35, zorder=0); ax3.set_axisbelow(True)
    for i, val in enumerate(pm.values):
        ax3.text(val + pm.max() * 0.012, i, fmt(val), va="center", fontsize=8, color=C["body"])

    # ── debit/credit/transfer pie ─────────────────────────────────────────────
    ax4 = fig.add_axes([0.57, 0.09, 0.38, 0.36])
    ax4.axis("off")
    add_chart_frame(ax4, "Debit / Credit / Transfer")
    td = df.groupby("Type")["Amount"].sum()
    ax4.pie(td.values, labels=td.index, autopct="%1.1f%%",
            colors=[C["danger"], C["success"], C["muted"]][:len(td)],
            wedgeprops={"linewidth": 2.5, "edgecolor": C["bg"]},
            startangle=90)

    pdf.savefig(fig, bbox_inches="tight")
    plt.close(fig)
