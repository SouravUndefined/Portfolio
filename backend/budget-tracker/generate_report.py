#!/usr/bin/env python3
"""
Generate a PDF spending report from spending_YYYYMM.csv

Usage:
    python generate_report.py local-database/budget-tracker/output/spending_202603.csv
    python generate_report.py local-database/budget-tracker/output   <- picks latest CSV automatically
"""

import os
import sys
import json
import glob
import warnings
import textwrap
from datetime import datetime
from dotenv import load_dotenv
load_dotenv()

import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

# Fix: matplotlib.path.Path.__deepcopy__ infinite recursion on Python 3.14
import copy, matplotlib.path as _mpath
def _path_deepcopy(self, memo):
    cls = type(self)
    result = cls.__new__(cls)
    memo[id(self)] = result
    for k, v in self.__dict__.items():
        setattr(result, k, copy.deepcopy(v, memo))
    return result
_mpath.Path.__deepcopy__ = _path_deepcopy
import matplotlib.gridspec as gridspec
from matplotlib.backends.backend_pdf import PdfPages
from matplotlib.patches import FancyBboxPatch
import matplotlib.ticker as mticker
import numpy as np

warnings.filterwarnings("ignore")

# ── palette ──────────────────────────────────────────────────────────────────
C = {
    "bg":       "#FAFAFA",
    "card":     "#FFFFFF",
    "primary":  "#2563EB",
    "secondary":"#7C3AED",
    "accent":   "#F59E0B",
    "danger":   "#EF4444",
    "success":  "#10B981",
    "text":     "#1E293B",
    "muted":    "#64748B",
    "border":   "#E2E8F0",
}

CAT_COLORS = [
    "#2563EB","#7C3AED","#F59E0B","#10B981","#EF4444",
    "#EC4899","#06B6D4","#84CC16","#F97316","#6366F1",
    "#14B8A6","#A855F7",
]

def _style():
    plt.rcParams.update({
        "figure.facecolor":  C["bg"],
        "axes.facecolor":    C["card"],
        "axes.edgecolor":    C["border"],
        "axes.labelcolor":   C["text"],
        "axes.titlecolor":   C["text"],
        "axes.titlesize":    11,
        "axes.labelsize":    9,
        "axes.spines.top":   False,
        "axes.spines.right": False,
        "xtick.color":       C["muted"],
        "ytick.color":       C["muted"],
        "xtick.labelsize":   8,
        "ytick.labelsize":   8,
        "grid.color":        C["border"],
        "grid.linewidth":    0.6,
        "text.color":        C["text"],
        "font.family":       "DejaVu Sans",
        "legend.fontsize":   8,
        "legend.framealpha": 0.85,
    })

def _fig(w=11.69, h=8.27):          # A4 landscape
    return plt.figure(figsize=(w, h), facecolor=C["bg"])

def _header(fig, title, subtitle=""):
    fig.text(0.5, 0.97, title,    ha="center", va="top",
             fontsize=16, fontweight="bold", color=C["text"])
    if subtitle:
        fig.text(0.5, 0.935, subtitle, ha="center", va="top",
                 fontsize=9, color=C["muted"])

def _stat_box(ax, label, value, color=None):
    ax.axis("off")
    ax.set_facecolor(color or C["primary"])
    ax.text(0.5, 0.62, value, ha="center", va="center", transform=ax.transAxes,
            fontsize=14, fontweight="bold", color="white")
    ax.text(0.5, 0.22, label, ha="center", va="center", transform=ax.transAxes,
            fontsize=8, color="white", alpha=0.85)
    for spine in ax.spines.values():
        spine.set_visible(False)

def fmt(n):
    if n >= 1_00_000:
        return f"Rs.{n/1_00_000:.1f}L"
    if n >= 1_000:
        return f"Rs.{n/1_000:.1f}K"
    return f"Rs.{n:.0f}"


# ── data helpers ──────────────────────────────────────────────────────────────

def load(csv_path):
    df = pd.read_csv(csv_path)
    df["Date"] = pd.to_datetime(df["Date"])
    return df

def debits(df):
    return df[df["Type"] == "Debit"].copy()

def credits(df):
    return df[df["Type"] == "Credit"].copy()


# ═══════════════════════════════════════════════════════════════════════════════
# PAGE 1 — EXECUTIVE SUMMARY
# ═══════════════════════════════════════════════════════════════════════════════

def page_summary(df, pdf):
    _style()
    fig = _fig()
    month_label = df["Date"].dt.strftime("%B %Y").mode()[0]
    _header(fig, f"Spending Report — {month_label}", "Personal Finance Summary")

    d  = debits(df);   c = credits(df)
    total_spent    = d["Amount"].sum()
    total_received = c["Amount"].sum()
    net            = total_spent - total_received
    n_txns         = len(df)
    avg_daily      = total_spent / max(df["Date"].nunique(), 1)
    biggest        = d.nlargest(1, "Amount").iloc[0] if len(d) else None
    n_sources      = df["Source"].nunique()

    # stat boxes
    gs = gridspec.GridSpec(3, 4, figure=fig,
                           top=0.88, bottom=0.54, hspace=0.35, wspace=0.25,
                           left=0.05, right=0.95)
    stats = [
        ("Total Spent",       fmt(total_spent),    C["danger"]),
        ("Total Received",    fmt(total_received),  C["success"]),
        ("Net Outflow",       fmt(net),             C["primary"]),
        ("Transactions",      str(n_txns),          C["secondary"]),
        ("Avg Daily Spend",   fmt(avg_daily),       C["accent"]),
        ("Biggest Transaction", fmt(biggest["Amount"]) if biggest is not None else "—", "#64748B"),
        ("Payment Sources",   str(n_sources),       "#0891B2"),
        ("Days with Spending",str(df["Date"].nunique()), "#059669"),
    ]
    for i, (lbl, val, col) in enumerate(stats):
        ax = fig.add_subplot(gs[i // 4, i % 4])
        _stat_box(ax, lbl, val, col)

    # category bar (bottom half)
    ax2 = fig.add_axes([0.05, 0.08, 0.55, 0.38])
    cat = d.groupby("Category")["Amount"].sum().sort_values(ascending=True).tail(10)
    bars = ax2.barh(cat.index, cat.values, color=CAT_COLORS[:len(cat)], height=0.65)
    ax2.set_title("Top Spending Categories", fontweight="bold", pad=8)
    ax2.set_xlabel("Amount (Rs.)")
    ax2.xaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: fmt(x)))
    ax2.grid(axis="x", alpha=0.4)
    for bar, val in zip(bars, cat.values):
        ax2.text(val + total_spent * 0.005, bar.get_y() + bar.get_height()/2,
                 fmt(val), va="center", fontsize=7.5, color=C["text"])

    # source pie (bottom right)
    ax3 = fig.add_axes([0.65, 0.08, 0.3, 0.38])
    src = d.groupby("Source")["Amount"].sum()
    wedges, texts, autotexts = ax3.pie(
        src.values, labels=None, autopct="%1.1f%%",
        colors=CAT_COLORS[:len(src)], startangle=90,
        wedgeprops={"linewidth": 1.5, "edgecolor": "white"}, pctdistance=0.75
    )
    for at in autotexts:
        at.set_fontsize(8); at.set_color("white"); at.set_fontweight("bold")
    ax3.legend(src.index, loc="lower center", bbox_to_anchor=(0.5, -0.18),
               ncol=1, fontsize=7.5)
    ax3.set_title("Spent by Source", fontweight="bold", pad=8)

    pdf.savefig(fig, bbox_inches="tight"); plt.close(fig)


# ═══════════════════════════════════════════════════════════════════════════════
# PAGE 2 — DAILY & WEEKLY TREND
# ═══════════════════════════════════════════════════════════════════════════════

def page_trends(df, pdf):
    _style()
    fig = _fig()
    month_label = df["Date"].dt.strftime("%B %Y").mode()[0]
    _header(fig, "Spending Trends", month_label)

    d = debits(df)

    # daily trend
    daily = d.groupby("Date")["Amount"].sum().reindex(
        pd.date_range(d["Date"].min(), d["Date"].max()), fill_value=0
    )

    ax1 = fig.add_axes([0.06, 0.55, 0.88, 0.33])
    ax1.fill_between(daily.index, daily.values, alpha=0.18, color=C["primary"])
    ax1.plot(daily.index, daily.values, color=C["primary"], linewidth=2)
    roll = daily.rolling(3, min_periods=1).mean()
    ax1.plot(roll.index, roll.values, color=C["danger"], linewidth=1.5,
             linestyle="--", label="3-day avg")
    ax1.set_title("Daily Spending", fontweight="bold", pad=8)
    ax1.set_ylabel("Amount (Rs.)")
    ax1.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: fmt(x)))
    tick_dates = daily.index[::3]
    ax1.set_xticks(tick_dates)
    ax1.set_xticklabels([d.strftime("%d %b") for d in tick_dates],
                        rotation=45, ha='right', fontsize=7)
    ax1.grid(axis="y", alpha=0.4)
    ax1.legend()

    # day-of-week
    ax2 = fig.add_axes([0.06, 0.08, 0.42, 0.35])
    dow_order = ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"]
    dow = d.groupby("Day_Name")["Amount"].sum().reindex(dow_order, fill_value=0)
    colors_dow = [C["accent"] if d in ("Saturday","Sunday") else C["primary"] for d in dow.index]
    bars = ax2.bar(range(len(dow)), dow.values, color=colors_dow, width=0.6)
    ax2.set_xticks(range(len(dow)))
    ax2.set_xticklabels([d[:3] for d in dow.index], rotation=0)
    ax2.set_title("Spending by Day of Week", fontweight="bold", pad=8)
    ax2.set_ylabel("Amount (Rs.)")
    ax2.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: fmt(x)))
    ax2.grid(axis="y", alpha=0.4)
    for bar, val in zip(bars, dow.values):
        if val > 0:
            ax2.text(bar.get_x() + bar.get_width()/2, val + dow.max()*0.01,
                     fmt(val), ha="center", fontsize=7, color=C["text"])

    # weekly buckets
    ax3 = fig.add_axes([0.56, 0.08, 0.38, 0.35])
    weekly = d.groupby("Week_Label")["Amount"].sum()
    ax3.bar(range(len(weekly)), weekly.values, color=C["secondary"], width=0.55)
    ax3.set_xticks(range(len(weekly)))
    ax3.set_xticklabels([w.replace(" - ", "\n") for w in weekly.index], fontsize=7)
    ax3.set_title("Spending by Week", fontweight="bold", pad=8)
    ax3.set_ylabel("Amount (Rs.)")
    ax3.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: fmt(x)))
    ax3.grid(axis="y", alpha=0.4)
    for i, val in enumerate(weekly.values):
        ax3.text(i, val + weekly.max()*0.01, fmt(val),
                 ha="center", fontsize=7.5, color=C["text"])

    pdf.savefig(fig, bbox_inches="tight"); plt.close(fig)


# ═══════════════════════════════════════════════════════════════════════════════
# PAGE 3 — CATEGORY DEEP DIVE
# ═══════════════════════════════════════════════════════════════════════════════

def page_categories(df, pdf):
    _style()
    fig = _fig()
    month_label = df["Date"].dt.strftime("%B %Y").mode()[0]
    _header(fig, "Category Breakdown", month_label)

    d = debits(df)
    cat = d.groupby("Category")["Amount"].sum().sort_values(ascending=False)
    total = cat.sum()

    # donut
    ax1 = fig.add_axes([0.02, 0.08, 0.38, 0.78])
    wedges, _, autotexts = ax1.pie(
        cat.values, labels=None, autopct=lambda p: f"{p:.1f}%" if p > 3 else "",
        colors=CAT_COLORS[:len(cat)], startangle=90, pctdistance=0.82,
        wedgeprops={"linewidth": 2, "edgecolor": "white"},
    )
    for at in autotexts:
        at.set_fontsize(7.5); at.set_fontweight("bold")
    centre = plt.Circle((0, 0), 0.55, color=C["bg"])
    ax1.add_patch(centre)
    ax1.text(0, 0.08, fmt(total), ha="center", va="center",
             fontsize=13, fontweight="bold", color=C["text"])
    ax1.text(0, -0.18, "Total Spent", ha="center", va="center",
             fontsize=8, color=C["muted"])
    ax1.set_title("Category Split", fontweight="bold", pad=8)

    # legend with amounts
    legend_labels = [f"{c}  ({fmt(v)}, {v/total*100:.1f}%)"
                     for c, v in zip(cat.index, cat.values)]
    ax1.legend(wedges, legend_labels, loc="lower center",
               bbox_to_anchor=(0.5, -0.22), ncol=2, fontsize=7)

    # subcategory bars for top 3 categories
    top3 = cat.head(3).index.tolist()
    positions = [(0.44, 0.63), (0.44, 0.37), (0.44, 0.11)]
    widths = [0.54, 0.54, 0.54]
    heights = [0.19, 0.19, 0.19]

    for idx, (cat_name, (x, y)) in enumerate(zip(top3, positions)):
        sub = d[d["Category"] == cat_name].groupby("Subcategory")["Amount"].sum()\
                .sort_values(ascending=True).tail(5)
        ax = fig.add_axes([x, y, widths[idx], heights[idx]])
        color = CAT_COLORS[list(cat.index).index(cat_name)]
        bars = ax.barh(sub.index, sub.values, color=color, height=0.5, alpha=0.85)
        ax.set_title(f"{cat_name}  ({fmt(cat[cat_name])})",
                     fontweight="bold", fontsize=9, pad=10, color=color)
        ax.xaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: fmt(x)))
        ax.grid(axis="x", alpha=0.3)
        for bar, val in zip(bars, sub.values):
            ax.text(val + sub.max() * 0.02, bar.get_y() + bar.get_height()/2,
                    fmt(val), va="center", fontsize=7)

    pdf.savefig(fig, bbox_inches="tight"); plt.close(fig)


# ═══════════════════════════════════════════════════════════════════════════════
# PAGE 4 — TOP MERCHANTS & AMOUNT DISTRIBUTION
# ═══════════════════════════════════════════════════════════════════════════════

def page_merchants(df, pdf):
    _style()
    fig = _fig()
    month_label = df["Date"].dt.strftime("%B %Y").mode()[0]
    _header(fig, "Top Merchants & Amount Distribution", month_label)

    d = debits(df)

    # top merchants by total
    ax1 = fig.add_axes([0.05, 0.55, 0.55, 0.35])
    top_m = d.groupby("Description")["Amount"].sum().sort_values(ascending=True).tail(12)
    colors_m = [CAT_COLORS[i % len(CAT_COLORS)] for i in range(len(top_m))]
    bars = ax1.barh(
        [textwrap.shorten(m, 30) for m in top_m.index],
        top_m.values, color=colors_m, height=0.6
    )
    ax1.set_title("Top Merchants by Total Spend", fontweight="bold", pad=8)
    ax1.xaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: fmt(x)))
    ax1.margins(x=0.18)
    ax1.grid(axis="x", alpha=0.4)
    for bar, val in zip(bars, top_m.values):
        ax1.text(val + top_m.max() * 0.01, bar.get_y() + bar.get_height()/2,
                 fmt(val), va="center", fontsize=7.5)

    # top by frequency
    ax2 = fig.add_axes([0.65, 0.55, 0.3, 0.35])
    top_freq = d["Description"].value_counts().head(8)
    ax2.barh(
        [textwrap.shorten(m, 22) for m in top_freq.index],
        top_freq.values, color=C["secondary"], height=0.6
    )
    ax2.set_title("Most Frequent Merchants", fontweight="bold", pad=8)
    ax2.set_xlabel("No. of Transactions")
    ax2.grid(axis="x", alpha=0.4)
    for i, val in enumerate(top_freq.values):
        ax2.text(val + 0.1, i, str(val), va="center", fontsize=7.5)

    # amount bucket distribution
    ax3 = fig.add_axes([0.05, 0.08, 0.42, 0.35])
    bucket_order = [
        "Rs.0-50 (Micro)", "Rs.51-200 (Small)", "Rs.201-500 (Medium)",
        "Rs.501-1000 (Large)", "Rs.1001-5000 (Major)", "Rs.5000+ (Mega)"
    ]
    bucket_counts = d["Amount_Bucket"].value_counts().reindex(bucket_order, fill_value=0)
    bucket_colors = [C["success"], C["primary"], C["accent"],
                     C["secondary"], C["danger"], "#7C3AED"]
    bars3 = ax3.bar(range(len(bucket_counts)), bucket_counts.values,
                    color=bucket_colors, width=0.6)
    ax3.set_xticks(range(len(bucket_counts)))
    ax3.set_xticklabels(
        [b.split(" ")[0] for b in bucket_counts.index], rotation=30, ha="right", fontsize=7
    )
    ax3.set_title("Transaction Size Distribution", fontweight="bold", pad=8)
    ax3.set_ylabel("Number of Transactions")
    ax3.grid(axis="y", alpha=0.4)
    for bar, val in zip(bars3, bucket_counts.values):
        ax3.text(bar.get_x() + bar.get_width()/2, val + 0.3,
                 str(val), ha="center", fontsize=8)

    # recurring vs one-time
    ax4 = fig.add_axes([0.58, 0.08, 0.36, 0.35])
    rec = d.groupby("Is_Recurring")["Amount"].agg(["sum","count"])
    labels_r = ["One-time", "Recurring"] if "No" in rec.index else list(rec.index)
    vals_r   = [rec.loc["No","sum"] if "No" in rec.index else 0,
                rec.loc["Yes","sum"] if "Yes" in rec.index else 0]
    ax4.pie(vals_r, labels=labels_r, autopct="%1.1f%%",
            colors=[C["primary"], C["accent"]],
            wedgeprops={"linewidth": 2, "edgecolor": "white"},
            startangle=90)
    ax4.set_title("Recurring vs One-time Spend", fontweight="bold", pad=8)

    pdf.savefig(fig, bbox_inches="tight"); plt.close(fig)


# ═══════════════════════════════════════════════════════════════════════════════
# PAGE 5 — SPEND TYPE & PAYMENT MODE
# ═══════════════════════════════════════════════════════════════════════════════

def page_spend_type(df, pdf):
    _style()
    fig = _fig()
    month_label = df["Date"].dt.strftime("%B %Y").mode()[0]
    _header(fig, "Essential vs Discretionary  |  Payment Modes", month_label)

    d = debits(df)

    # essential vs discretionary stacked by category
    ax1 = fig.add_axes([0.05, 0.55, 0.55, 0.35])
    st = d.groupby(["Spend_Type","Category"])["Amount"].sum().unstack(level=0, fill_value=0)
    cats = st.sum(axis=1).sort_values(ascending=True).index
    st   = st.loc[cats]
    x    = range(len(cats))
    bottom = np.zeros(len(cats))
    for col, color in zip(st.columns, [C["primary"], C["accent"]]):
        if col in st:
            ax1.barh(list(x), st[col].values, left=bottom, label=col,
                     color=color, height=0.55, alpha=0.85)
            bottom += st[col].values
    ax1.set_yticks(list(x))
    ax1.set_yticklabels([textwrap.shorten(c, 22) for c in cats], fontsize=7.5)
    ax1.set_title("Essential vs Discretionary by Category", fontweight="bold", pad=8)
    ax1.xaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: fmt(x)))
    ax1.legend(loc="lower right"); ax1.grid(axis="x", alpha=0.3)

    # big pie: essential vs discretionary overall
    ax2 = fig.add_axes([0.65, 0.55, 0.3, 0.35])
    ess = d.groupby("Spend_Type")["Amount"].sum()
    ax2.pie(ess.values, labels=ess.index, autopct="%1.1f%%",
            colors=[C["primary"], C["accent"]],
            wedgeprops={"linewidth": 2, "edgecolor": "white"}, startangle=90)
    ax2.set_title("Spend Type Split", fontweight="bold", pad=8)

    # payment mode bar
    ax3 = fig.add_axes([0.05, 0.08, 0.42, 0.35])
    pm = d.groupby("Payment_Mode")["Amount"].sum().sort_values(ascending=True)
    ax3.barh(pm.index, pm.values,
             color=[C["primary"], C["secondary"], C["success"], C["accent"]][:len(pm)],
             height=0.55)
    ax3.set_title("Spending by Payment Mode", fontweight="bold", pad=8)
    ax3.xaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: fmt(x)))
    ax3.grid(axis="x", alpha=0.4)
    for i, val in enumerate(pm.values):
        ax3.text(val + pm.max()*0.01, i, fmt(val), va="center", fontsize=8)

    # credit vs debit vs transfer breakdown
    ax4 = fig.add_axes([0.58, 0.08, 0.36, 0.35])
    td = df.groupby("Type")["Amount"].sum()
    ax4.pie(td.values, labels=td.index, autopct="%1.1f%%",
            colors=[C["danger"], C["success"], C["muted"]][:len(td)],
            wedgeprops={"linewidth": 2, "edgecolor": "white"}, startangle=90)
    ax4.set_title("Debit / Credit / Transfer", fontweight="bold", pad=8)

    pdf.savefig(fig, bbox_inches="tight"); plt.close(fig)


# ═══════════════════════════════════════════════════════════════════════════════
# PAGE 6 — KEY INSIGHTS
# ═══════════════════════════════════════════════════════════════════════════════

def page_insights(df, pdf):
    _style()
    fig = _fig()
    month_label = df["Date"].dt.strftime("%B %Y").mode()[0]
    _header(fig, "Key Insights & Highlights", month_label)

    d  = debits(df)
    c  = credits(df)
    total_spent = d["Amount"].sum()

    insights = []

    # 1. Biggest day
    by_day = d.groupby("Date")["Amount"].sum()
    if len(by_day):
        max_day = by_day.idxmax()
        insights.append(("Biggest Spending Day",
            f"{max_day.strftime('%d %b %Y')} — {fmt(by_day.max())} spent "
            f"({by_day.max()/total_spent*100:.1f}% of monthly total)"))

    # 2. Top category
    top_cat = d.groupby("Category")["Amount"].sum().idxmax()
    top_cat_amt = d.groupby("Category")["Amount"].sum().max()
    insights.append(("Highest Spend Category",
        f"{top_cat} — {fmt(top_cat_amt)} ({top_cat_amt/total_spent*100:.1f}% of total)"))

    # 3. Weekend vs weekday
    d2 = d.copy(); d2["is_wknd"] = d2["Is_Weekend"] == "Yes"
    wknd_avg = d2[d2.is_wknd]["Amount"].mean() if d2[d2.is_wknd].shape[0] else 0
    wkdy_avg = d2[~d2.is_wknd]["Amount"].mean() if d2[~d2.is_wknd].shape[0] else 0
    if wknd_avg and wkdy_avg:
        ratio = wknd_avg / wkdy_avg
        txt = f"Weekend avg transaction Rs.{wknd_avg:,.0f} vs weekday Rs.{wkdy_avg:,.0f} "
        txt += f"— {'weekends cost {:.0f}% more per transaction'.format((ratio-1)*100) if ratio > 1 else 'weekdays cost {:.0f}% more per transaction'.format((1/ratio-1)*100)}"
        insights.append(("Weekend vs Weekday", txt))

    # 4. Recurring subscriptions
    rec_total = d[d["Is_Recurring"] == "Yes"]["Amount"].sum()
    rec_count = d[d["Is_Recurring"] == "Yes"]["Description"].nunique()
    if rec_total > 0:
        insights.append(("Recurring Subscriptions",
            f"Rs.{rec_total:,.2f} across {rec_count} recurring services "
            f"({rec_total/total_spent*100:.1f}% of total spend)"))

    # 5. Largest single transaction
    if len(d):
        big = d.nlargest(1, "Amount").iloc[0]
        insights.append(("Largest Single Transaction",
            f"{fmt(big['Amount'])} — {big['Description']} on {pd.Timestamp(big['Date']).strftime('%d %b')}"))

    # 6. Most used payment source
    top_src = d.groupby("Source")["Amount"].sum().idxmax()
    top_src_pct = d.groupby("Source")["Amount"].sum().max() / total_spent * 100
    insights.append(("Primary Payment Source",
        f"{top_src} — {top_src_pct:.1f}% of total spend"))

    # 7. Cashback/credits received
    if len(c) and c["Amount"].sum() > 0:
        insights.append(("Cashback & Credits Received",
            f"Rs.{c['Amount'].sum():,.2f} received ({len(c)} credit transactions) — "
            f"effective net spend: {fmt(total_spent - c['Amount'].sum())}"))

    # 8. Zero-spend days
    all_days = pd.date_range(d["Date"].min(), d["Date"].max())
    spend_days = d["Date"].dt.normalize().nunique()
    zero_days  = len(all_days) - spend_days
    insights.append(("Days Without Spending",
        f"{zero_days} days out of {len(all_days)} had no recorded spend"))

    # 9. Small transactions (micro-spend)
    micro = d[d["Amount"] <= 50]
    if len(micro):
        insights.append(("Micro Transactions (≤ Rs.50)",
            f"{len(micro)} transactions totalling Rs.{micro['Amount'].sum():,.2f} "
            f"— consider if these are worth tracking individually"))

    # 10. Top day-of-week for spending
    dow_total = d.groupby("Day_Name")["Amount"].sum()
    if len(dow_total):
        top_dow = dow_total.idxmax()
        insights.append(("Most Expensive Day of Week",
            f"{top_dow} — {fmt(dow_total.max())} total this month"))

    # render insights as text cards
    n = len(insights)
    cols = 2
    rows = (n + 1) // cols
    for idx, (title, body) in enumerate(insights):
        col = idx % cols
        row = idx // cols
        pad_top    = 0.06
        pad_left   = 0.04
        cell_w     = (1 - pad_left * 2 - 0.04) / cols
        cell_h     = (0.84 - pad_top) / rows
        x = pad_left + col * (cell_w + 0.04)
        y = 0.88 - (row + 1) * cell_h

        ax = fig.add_axes([x, y, cell_w, cell_h * 0.88])
        ax.axis("off")
        ax.set_facecolor(C["card"])
        for spine in ax.spines.values():
            spine.set_visible(False)

        # coloured left bar
        bar_color = CAT_COLORS[idx % len(CAT_COLORS)]
        ax.plot([0.01, 0.01], [0.1, 0.9], linewidth=4,
                color=bar_color, transform=ax.transAxes, clip_on=False)

        ax.text(0.05, 0.72, f"  {title}", transform=ax.transAxes,
                fontsize=9, fontweight="bold", color=bar_color, va="top")
        wrapped = textwrap.fill(body, width=72)
        ax.text(0.05, 0.45, f"  {wrapped}", transform=ax.transAxes,
                fontsize=8, color=C["text"], va="top", linespacing=1.4)

    pdf.savefig(fig, bbox_inches="tight"); plt.close(fig)


# ═══════════════════════════════════════════════════════════════════════════════
# PAGE 7 — ADVANCED ANALYTICS
# ═══════════════════════════════════════════════════════════════════════════════

def page_advanced(df, pdf):
    _style()
    fig = _fig()
    month_label = df["Date"].dt.strftime("%B %Y").mode()[0]
    _header(fig, "Advanced Analytics", month_label)

    d = debits(df)
    total_spent = d["Amount"].sum()

    # ── cumulative spend curve ────────────────────────────────────────────────
    ax1 = fig.add_axes([0.05, 0.55, 0.55, 0.33])
    daily = d.groupby("Date")["Amount"].sum().reindex(
        pd.date_range(d["Date"].min(), d["Date"].max()), fill_value=0
    )
    cumsum = daily.cumsum()
    days   = np.arange(1, len(cumsum) + 1)
    ideal  = np.linspace(0, total_spent, len(days))   # straight line = even spend

    ax1.fill_between(days, cumsum.values, alpha=0.15, color=C["primary"])
    ax1.plot(days, cumsum.values, color=C["primary"], linewidth=2, label="Actual")
    ax1.plot(days, ideal,         color=C["muted"],   linewidth=1.5,
             linestyle="--", label="Even pace")

    # shade overspend zones (actual above ideal)
    ax1.fill_between(days,
                     np.where(cumsum.values > ideal, cumsum.values, ideal),
                     ideal,
                     alpha=0.25, color=C["danger"], label="Ahead of pace")

    ax1.set_title("Cumulative Spending Curve", fontweight="bold", pad=8)
    ax1.set_xlabel("Day of Month")
    ax1.set_ylabel("Cumulative Spend (Rs.)")
    ax1.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: fmt(x)))
    ax1.legend(fontsize=7.5); ax1.grid(alpha=0.3)

    # ── spending heatmap (week × day-of-week) ─────────────────────────────────
    ax2 = fig.add_axes([0.65, 0.55, 0.3, 0.33])
    d2  = d.copy()
    d2["week_num"] = d2["Date"].dt.isocalendar().week
    d2["dow"]      = d2["Date"].dt.dayofweek
    pivot = d2.pivot_table(values="Amount", index="week_num", columns="dow",
                           aggfunc="sum", fill_value=0)
    pivot.columns = ["Mon","Tue","Wed","Thu","Fri","Sat","Sun"]

    im = ax2.imshow(pivot.values, aspect="auto", cmap="YlOrRd",
                    interpolation="nearest")
    ax2.set_xticks(range(len(pivot.columns)))
    ax2.set_xticklabels(pivot.columns, fontsize=7.5)
    ax2.set_yticks(range(len(pivot.index)))
    ax2.set_yticklabels([f"Wk {w}" for w in pivot.index], fontsize=7.5)
    ax2.set_title("Spending Heatmap (Week × Day)", fontweight="bold", pad=8)
    for i in range(pivot.shape[0]):
        for j in range(pivot.shape[1]):
            v = pivot.values[i, j]
            if v > 0:
                ax2.text(j, i, fmt(v), ha="center", va="center",
                         fontsize=5.5, color="black" if v < pivot.values.max()*0.6 else "white")
    plt.colorbar(im, ax=ax2, fraction=0.046, pad=0.04).ax.tick_params(labelsize=6)

    # ── category week-over-week stacked area ──────────────────────────────────
    ax3 = fig.add_axes([0.05, 0.08, 0.55, 0.33])
    d3  = d.copy()
    d3["week_label"] = d3["Week_Label"]
    top5_cats  = d.groupby("Category")["Amount"].sum().nlargest(5).index.tolist()
    weekly_cat = d3[d3["Category"].isin(top5_cats)].groupby(
        ["Week_Label", "Category"])["Amount"].sum().unstack(fill_value=0)
    weekly_cat = weekly_cat.reindex(columns=top5_cats, fill_value=0)

    x_pos = range(len(weekly_cat))
    bottom = np.zeros(len(weekly_cat))
    for i, cat in enumerate(top5_cats):
        vals = weekly_cat[cat].values if cat in weekly_cat.columns else np.zeros(len(weekly_cat))
        ax3.bar(x_pos, vals, bottom=bottom, label=cat,
                color=CAT_COLORS[i], width=0.65, alpha=0.88)
        bottom += vals

    ax3.set_xticks(list(x_pos))
    ax3.set_xticklabels([w.replace(" - ", "\n") for w in weekly_cat.index], fontsize=7)
    ax3.set_title("Top 5 Categories — Week by Week", fontweight="bold", pad=8)
    ax3.set_ylabel("Amount (Rs.)")
    ax3.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: fmt(x)))
    ax3.legend(fontsize=7, loc="upper right"); ax3.grid(axis="y", alpha=0.3)

    # ── avg spend per transaction by category ─────────────────────────────────
    ax4 = fig.add_axes([0.65, 0.08, 0.3, 0.33])
    avg_txn = d.groupby("Category").agg(total=("Amount","sum"),
                                         count=("Amount","count"))
    avg_txn["avg"] = avg_txn["total"] / avg_txn["count"]
    avg_txn = avg_txn.sort_values("avg", ascending=True).tail(8)
    colors_avg = [CAT_COLORS[i % len(CAT_COLORS)] for i in range(len(avg_txn))]
    ax4.barh(avg_txn.index, avg_txn["avg"].values, color=colors_avg, height=0.55)
    ax4.set_title("Avg Transaction Size\nby Category", fontweight="bold", pad=8)
    ax4.xaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: fmt(x)))
    ax4.grid(axis="x", alpha=0.3)
    for i, val in enumerate(avg_txn["avg"].values):
        ax4.text(val + avg_txn["avg"].max()*0.01, i, fmt(val), va="center", fontsize=7.5)

    pdf.savefig(fig, bbox_inches="tight"); plt.close(fig)


# ═══════════════════════════════════════════════════════════════════════════════
# PAGE 8 — CASH FLOW & TRANSACTION PROFILE
# ═══════════════════════════════════════════════════════════════════════════════

def page_cashflow(df, pdf):
    _style()
    fig = _fig()
    month_label = df["Date"].dt.strftime("%B %Y").mode()[0]
    _header(fig, "Cash Flow & Transaction Profile", month_label)

    d = debits(df);  c = credits(df)

    # ── daily inflow vs outflow ───────────────────────────────────────────────
    ax1 = fig.add_axes([0.05, 0.55, 0.88, 0.33])
    date_range = pd.date_range(df["Date"].min(), df["Date"].max())
    daily_out = d.groupby("Date")["Amount"].sum().reindex(date_range, fill_value=0)
    daily_in  = c.groupby("Date")["Amount"].sum().reindex(date_range, fill_value=0)
    net_daily = daily_in - daily_out
    x = np.arange(len(date_range))

    ax1.bar(x, -daily_out.values, color=C["danger"],  alpha=0.75, label="Outflow",  width=0.6)
    ax1.bar(x,  daily_in.values,  color=C["success"], alpha=0.75, label="Inflow",   width=0.6)
    ax1.plot(x, net_daily.values, color=C["primary"], linewidth=2, label="Net",     zorder=5)
    ax1.axhline(0, color=C["muted"], linewidth=0.8, linestyle="--")
    ax1.set_xticks(x[::2])
    ax1.set_xticklabels([d.strftime("%d %b") for d in date_range[::2]], rotation=45, ha="right", fontsize=7)
    ax1.yaxis.set_major_formatter(mticker.FuncFormatter(lambda v, _: fmt(abs(v))))
    ax1.set_title("Daily Cash Flow — Inflow vs Outflow", fontweight="bold", pad=8)
    ax1.legend(fontsize=8); ax1.grid(axis="y", alpha=0.3)

    # ── transaction count by category ────────────────────────────────────────
    ax2 = fig.add_axes([0.05, 0.08, 0.28, 0.35])
    cnt = d.groupby("Category")["Amount"].count().sort_values(ascending=True).tail(8)
    ax2.barh(cnt.index, cnt.values, color=C["primary"], height=0.55, alpha=0.85)
    ax2.set_title("Transaction Count\nby Category", fontweight="bold", pad=8)
    ax2.set_xlabel("No. of Transactions")
    ax2.grid(axis="x", alpha=0.3)
    for i, v in enumerate(cnt.values):
        ax2.text(v + 0.1, i, str(v), va="center", fontsize=8)

    # ── spend velocity: first half vs second half ─────────────────────────────
    ax3 = fig.add_axes([0.38, 0.08, 0.28, 0.35])
    mid   = df["Date"].min() + (df["Date"].max() - df["Date"].min()) / 2
    first = d[d["Date"] <= mid]["Amount"].sum()
    second= d[d["Date"] >  mid]["Amount"].sum()
    bars  = ax3.bar(["First Half", "Second Half"], [first, second],
                    color=[C["primary"], C["secondary"]], width=0.5)
    ax3.set_title("First Half vs\nSecond Half Spending", fontweight="bold", pad=8)
    ax3.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: fmt(x)))
    ax3.grid(axis="y", alpha=0.3)
    for bar, val in zip(bars, [first, second]):
        ax3.text(bar.get_x() + bar.get_width()/2, val + max(first,second)*0.01,
                 fmt(val), ha="center", fontsize=9, fontweight="bold")
    pct = first / (first + second) * 100
    ax3.text(0.5, 0.05, f"{pct:.0f}% spent in first half",
             ha="center", transform=ax3.transAxes, fontsize=8, color=C["muted"])

    # ── top individual transactions table ─────────────────────────────────────
    ax4 = fig.add_axes([0.70, 0.08, 0.27, 0.35])
    ax4.axis("off")
    top10 = d.nlargest(8, "Amount")[["Date","Description","Amount"]].copy()
    top10["Date"]        = pd.to_datetime(top10["Date"]).dt.strftime("%d %b")
    top10["Description"] = top10["Description"].str[:20]
    top10["Amount"]      = top10["Amount"].apply(lambda x: f"Rs.{x:,.0f}")
    ax4.set_title("Top Transactions", fontweight="bold", pad=8, loc="left")
    table = ax4.table(
        cellText=top10.values,
        colLabels=["Date", "Description", "Amount"],
        cellLoc="left", loc="upper left",
        bbox=[0, 0, 1, 1]
    )
    table.auto_set_font_size(False)
    table.set_fontsize(7.5)
    for (r, c_), cell in table.get_celld().items():
        cell.set_edgecolor(C["border"])
        if r == 0:
            cell.set_facecolor(C["primary"])
            cell.set_text_props(color="white", fontweight="bold")
        elif r % 2 == 0:
            cell.set_facecolor("#F0F4FF")
        else:
            cell.set_facecolor(C["card"])

    pdf.savefig(fig, bbox_inches="tight"); plt.close(fig)


# ═══════════════════════════════════════════════════════════════════════════════
# PAGE 9 — AI FINANCIAL ADVISOR  (Groq / Llama 4 Scout)
# ═══════════════════════════════════════════════════════════════════════════════

def build_spending_summary(df):
    d = debits(df);  c = credits(df)
    total = d["Amount"].sum()
    month = df["Date"].dt.strftime("%B %Y").mode()[0]

    lines = [f"Month: {month}", f"Total Spent: Rs.{total:,.2f}",
             f"Total Received: Rs.{c['Amount'].sum():,.2f}",
             f"Transactions: {len(d)} debits, {len(c)} credits",
             "", "Spending by Category:"]
    for cat, amt in d.groupby("Category")["Amount"].sum().sort_values(ascending=False).items():
        lines.append(f"  {cat}: Rs.{amt:,.2f} ({amt/total*100:.1f}%)")

    lines += ["", "Top 5 Merchants:"]
    for desc, amt in d.groupby("Description")["Amount"].sum().nlargest(5).items():
        lines.append(f"  {desc}: Rs.{amt:,.2f}")

    lines += [
        "",
        f"Recurring subscriptions: Rs.{d[d['Is_Recurring']=='Yes']['Amount'].sum():,.2f}",
        f"Essential spending: Rs.{d[d['Spend_Type']=='Essential']['Amount'].sum():,.2f}",
        f"Discretionary spending: Rs.{d[d['Spend_Type']=='Discretionary']['Amount'].sum():,.2f}",
        f"Weekend spending: Rs.{d[d['Is_Weekend']=='Yes']['Amount'].sum():,.2f}",
        f"Weekday spending: Rs.{d[d['Is_Weekend']=='No']['Amount'].sum():,.2f}",
    ]
    return "\n".join(lines)


AI_PROMPT = """You are a personal finance advisor analyzing someone's spending for the month.

Based on the spending data below, provide a structured financial analysis in JSON format:

{
  "health_score": <integer 1-10 where 10 = excellent financial health>,
  "health_verdict": "<one sentence verdict on their financial health>",
  "advice": [
    {"title": "...", "detail": "...", "impact": "High/Medium/Low"}
  ],
  "missing": [
    {"category": "...", "why_important": "...", "suggested_amount": "..."}
  ],
  "recommendations": [
    {"action": "...", "target": "...", "reasoning": "..."}
  ],
  "budget_next_month": [
    {"category": "...", "current": "Rs.X", "suggested": "Rs.Y", "change": "+X% or -X%"}
  ],
  "positive_habits": ["...", "..."]
}

Rules:
- advice: 4-5 specific actionable tips based on ACTUAL numbers in the data
- missing: 3-4 important financial categories with ZERO or very low spending (e.g. investments, emergency fund, health insurance, savings)
- recommendations: 4-5 concrete actions for next month with specific amounts in Rs.
- budget_next_month: suggested budget for top 6 categories with percentage change
- positive_habits: 2-3 things they are doing well
- All amounts must be in Indian Rupees (Rs.)
- Be specific — reference actual categories and amounts from the data

Spending Data:
"""


def get_ai_advice(df):
    api_key  = os.environ.get("API_KEY") or os.environ.get("OPENAI_API_KEY")
    base_url = os.environ.get("BASE_URL", "").strip() or None
    model    = os.environ.get("MODEL", "gpt-4o-mini").strip()

    if not api_key:
        return None

    from openai import OpenAI
    kwargs = {"api_key": api_key}
    if base_url:
        kwargs["base_url"] = base_url
    client = OpenAI(**kwargs)

    summary = build_spending_summary(df)

    try:
        resp = client.chat.completions.create(
            model=model, temperature=0.3,
            response_format={"type": "json_object"},
            messages=[
                {"role": "system", "content": "You are a personal finance advisor. Return only valid JSON."},
                {"role": "user",   "content": AI_PROMPT + summary},
            ],
        )
        return json.loads(resp.choices[0].message.content)
    except Exception as e:
        print(f"  [AI] Could not get advice: {e}")
        return None


def page_ai_advisor(df, pdf, advice):
    _style()

    if advice is None:
        return

    month_label = df["Date"].dt.strftime("%B %Y").mode()[0]

    # ── PAGE A: Score + Advice + Missing ──────────────────────────────────────
    fig = _fig()
    _header(fig, "AI Financial Advisor", f"Personalized analysis for {month_label}")

    score   = advice.get("health_score", 5)
    verdict = advice.get("health_verdict", "")

    # score gauge (top-left)
    ax_score = fig.add_axes([0.03, 0.72, 0.18, 0.18])
    ax_score.axis("off")
    score_color = C["success"] if score >= 7 else C["accent"] if score >= 5 else C["danger"]
    circle = plt.Circle((0.5, 0.5), 0.42, color=score_color, zorder=2)
    bg     = plt.Circle((0.5, 0.5), 0.48, color=C["border"],  zorder=1)
    ax_score.add_patch(bg); ax_score.add_patch(circle)
    ax_score.text(0.5, 0.55, str(score), ha="center", va="center",
                  fontsize=28, fontweight="bold", color="white", zorder=3)
    ax_score.text(0.5, 0.18, "/ 10", ha="center", fontsize=10,
                  color="white", zorder=3)
    ax_score.set_xlim(0,1); ax_score.set_ylim(0,1)
    ax_score.set_title("Financial\nHealth Score", fontweight="bold",
                        fontsize=9, pad=4, color=score_color)

    # verdict
    ax_v = fig.add_axes([0.23, 0.76, 0.73, 0.10])
    ax_v.axis("off")
    ax_v.set_facecolor(score_color + "22")
    wrapped_v = textwrap.fill(verdict, width=100)
    ax_v.text(0.02, 0.5, wrapped_v, transform=ax_v.transAxes,
              fontsize=10, va="center", color=C["text"], style="italic")

    # positive habits
    habits = advice.get("positive_habits", [])
    ax_h = fig.add_axes([0.03, 0.63, 0.93, 0.10])
    ax_h.axis("off")
    ax_h.set_facecolor(C["success"] + "18")
    habit_txt = "  DOING WELL:   " + "   |   ".join(f"✓ {h}" for h in habits)
    ax_h.text(0.01, 0.5, habit_txt, transform=ax_h.transAxes,
              fontsize=8.5, va="center", color=C["success"], fontweight="bold")

    # advice cards
    adv_list = advice.get("advice", [])
    n_adv    = min(len(adv_list), 5)
    impact_colors = {"High": C["danger"], "Medium": C["accent"], "Low": C["success"]}

    ax_adv_title = fig.add_axes([0.03, 0.575, 0.47, 0.04])
    ax_adv_title.axis("off")
    ax_adv_title.text(0, 0.5, "ADVICE TO MANAGE SPENDING",
                      fontsize=10, fontweight="bold", color=C["primary"], va="center")

    for i, a in enumerate(adv_list[:n_adv]):
        y = 0.55 - i * 0.105
        ax = fig.add_axes([0.03, y - 0.085, 0.46, 0.09])
        ax.axis("off")
        ax.set_facecolor("#F8FAFF")
        ic = impact_colors.get(a.get("impact","Medium"), C["accent"])
        ax.plot([0.008, 0.008], [0.1, 0.9], linewidth=5, color=ic,
                transform=ax.transAxes, clip_on=False)
        ax.text(0.03, 0.75, a.get("title",""), transform=ax.transAxes,
                fontsize=8.5, fontweight="bold", color=C["text"], va="top")
        ax.text(0.03, 0.42, textwrap.fill(a.get("detail",""), 58),
                transform=ax.transAxes, fontsize=7.5, color=C["muted"], va="top")
        impact_lbl = a.get("impact","")
        ax.text(0.96, 0.75, impact_lbl, transform=ax.transAxes,
                fontsize=7, color=ic, fontweight="bold", ha="right", va="top")

    # missing categories
    miss_list = advice.get("missing", [])
    ax_miss_title = fig.add_axes([0.53, 0.575, 0.44, 0.04])
    ax_miss_title.axis("off")
    ax_miss_title.text(0, 0.5, "WHAT IS LACKING IN YOUR SPENDING",
                       fontsize=10, fontweight="bold", color=C["danger"], va="center")

    for i, m in enumerate(miss_list[:4]):
        y = 0.55 - i * 0.13
        ax = fig.add_axes([0.53, y - 0.105, 0.44, 0.115])
        ax.axis("off")
        ax.set_facecolor("#FFF8F8")
        ax.plot([0.008, 0.008], [0.1, 0.9], linewidth=5, color=C["danger"],
                transform=ax.transAxes, clip_on=False)
        ax.text(0.03, 0.82, m.get("category",""), transform=ax.transAxes,
                fontsize=8.5, fontweight="bold", color=C["danger"], va="top")
        ax.text(0.03, 0.55, textwrap.fill(m.get("why_important",""), 52),
                transform=ax.transAxes, fontsize=7.5, color=C["text"], va="top")
        suggested = m.get("suggested_amount","")
        if suggested:
            ax.text(0.03, 0.18, f"Suggested: {suggested}", transform=ax.transAxes,
                    fontsize=7.5, color=C["success"], fontweight="bold", va="top")

    pdf.savefig(fig, bbox_inches="tight"); plt.close(fig)

    # ── PAGE B: Recommendations + Budget Table ────────────────────────────────
    fig2 = _fig()
    _header(fig2, "Recommendations & Budget Plan", f"Action plan for next month")

    # recommendations
    recs = advice.get("recommendations", [])
    ax_r_title = fig2.add_axes([0.03, 0.88, 0.93, 0.04])
    ax_r_title.axis("off")
    ax_r_title.text(0, 0.5, "RECOMMENDATIONS FOR NEXT MONTH",
                    fontsize=11, fontweight="bold", color=C["secondary"], va="center")

    n_recs = min(len(recs), 5)
    for i, r in enumerate(recs[:n_recs]):
        col   = i % 2
        row   = i // 2
        x_pos = 0.03 + col * 0.50
        y_pos = 0.71 - row * 0.175
        ax = fig2.add_axes([x_pos, y_pos, 0.46, 0.155])
        ax.axis("off")
        ax.set_facecolor("#F5F3FF")
        # number badge
        ax.text(0.025, 0.75, str(i+1), transform=ax.transAxes,
                fontsize=18, fontweight="bold", color=C["secondary"]+"44", va="top")
        ax.text(0.10, 0.82, r.get("action",""), transform=ax.transAxes,
                fontsize=8.5, fontweight="bold", color=C["secondary"], va="top")
        target = r.get("target","")
        if target:
            ax.text(0.10, 0.58, f"Target: {target}", transform=ax.transAxes,
                    fontsize=8, color=C["primary"], fontweight="bold", va="top")
        ax.text(0.10, 0.35, textwrap.fill(r.get("reasoning",""), 60),
                transform=ax.transAxes, fontsize=7.5, color=C["muted"], va="top")

    # budget comparison table
    budget = advice.get("budget_next_month", [])
    if budget:
        ax_b_title = fig2.add_axes([0.03, 0.23, 0.93, 0.04])
        ax_b_title.axis("off")
        ax_b_title.text(0, 0.5, "SUGGESTED BUDGET FOR NEXT MONTH",
                        fontsize=11, fontweight="bold", color=C["primary"], va="center")

        ax_b = fig2.add_axes([0.03, 0.04, 0.93, 0.18])
        ax_b.axis("off")

        headers = ["Category", "This Month", "Next Month (Target)", "Change"]
        rows_data = [[b.get("category",""), b.get("current",""),
                      b.get("suggested",""), b.get("change","")]
                     for b in budget[:7]]

        table = ax_b.table(
            cellText=rows_data,
            colLabels=headers,
            cellLoc="center", loc="upper center",
            bbox=[0, 0, 1, 1]
        )
        table.auto_set_font_size(False)
        table.set_fontsize(9)
        col_widths = [0.35, 0.20, 0.25, 0.20]
        for (r2, c2), cell in table.get_celld().items():
            cell.set_edgecolor(C["border"])
            cell.set_linewidth(0.5)
            w = col_widths[c2] if c2 < len(col_widths) else 0.25
            cell.set_width(w)
            if r2 == 0:
                cell.set_facecolor(C["primary"])
                cell.set_text_props(color="white", fontweight="bold")
            elif r2 % 2 == 0:
                cell.set_facecolor("#F0F4FF")
            else:
                cell.set_facecolor(C["card"])
            # colour the change column
            if c2 == 3 and r2 > 0:
                txt = rows_data[r2-1][3] if r2-1 < len(rows_data) else ""
                if txt.startswith("-"):
                    cell.set_text_props(color=C["success"], fontweight="bold")
                elif txt.startswith("+"):
                    cell.set_text_props(color=C["danger"], fontweight="bold")

    pdf.savefig(fig2, bbox_inches="tight"); plt.close(fig2)


# ═══════════════════════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════════════════════

def find_csv(path):
    if os.path.isfile(path) and path.endswith(".csv"):
        return path
    if os.path.isdir(path):
        files = sorted(glob.glob(os.path.join(path, "spending_*.csv")))
        if files:
            return files[-1]
    raise FileNotFoundError(f"No spending CSV found at: {path}")


def generate(csv_path: str, output_path: str) -> None:
    """Callable entry point for Lambda / programmatic use."""
    df = load(csv_path)
    advice = get_ai_advice(df)
    with PdfPages(output_path) as pdf:
        page_summary(df, pdf)
        page_trends(df, pdf)
        page_categories(df, pdf)
        page_merchants(df, pdf)
        page_spend_type(df, pdf)
        page_insights(df, pdf)
        page_advanced(df, pdf)
        page_cashflow(df, pdf)
        page_ai_advisor(df, pdf, advice)
        meta = pdf.infodict()
        meta["Title"]  = f"Spending Report"
        meta["Author"] = "Spending Pipeline"
        meta["CreationDate"] = datetime.now()


def main():
    output_folder = os.environ.get("OUTPUT_FOLDER", "../../local-database/budget-tracker/output")
    target   = sys.argv[1] if len(sys.argv) >= 2 else output_folder
    csv_path = find_csv(target)

    df = load(csv_path)
    month_tag = df["Date"].dt.strftime("%Y%m").mode()[0]
    out_pdf = os.path.join(output_folder, f"spending_report_{month_tag}.pdf")

    print(f"  Source  : {csv_path}")
    print(f"  Records : {len(df)} rows")
    print(f"  Output  : {out_pdf}")
    print()

    print("  Fetching AI financial advice from Groq ...")
    advice = get_ai_advice(df)
    if advice:
        print("  AI advice ready.")
    else:
        print("  AI advice unavailable — skipping advisor pages.")

    with PdfPages(out_pdf) as pdf:
        print("  [1/9] Summary page ...")
        page_summary(df, pdf)

        print("  [2/9] Trend charts ...")
        page_trends(df, pdf)

        print("  [3/9] Category breakdown ...")
        page_categories(df, pdf)

        print("  [4/9] Merchants & distribution ...")
        page_merchants(df, pdf)

        print("  [5/9] Spend type & payment mode ...")
        page_spend_type(df, pdf)

        print("  [6/9] Key insights ...")
        page_insights(df, pdf)

        print("  [7/9] Advanced analytics ...")
        page_advanced(df, pdf)

        print("  [8/9] Cash flow & transaction profile ...")
        page_cashflow(df, pdf)

        print("  [9/9] AI financial advisor ...")
        page_ai_advisor(df, pdf, advice)

        meta = pdf.infodict()
        meta["Title"]   = f"Spending Report {month_tag}"
        meta["Author"]  = "Spending Pipeline"
        meta["Subject"] = "Personal Finance Report"
        meta["CreationDate"] = datetime.now()

    n_pages = 8 + (2 if advice else 0)
    print(f"\n  Done! Report saved to: {out_pdf}")
    print(f"  Pages: {n_pages}")


if __name__ == "__main__":
    main()
