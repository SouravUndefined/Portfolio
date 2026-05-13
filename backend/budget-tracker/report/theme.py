"""
Shared visual theme, style helpers, and formatters used by every page module.
"""

import copy
import warnings

import matplotlib
matplotlib.use("Agg")
import matplotlib.path as _mpath
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
from matplotlib.patches import FancyBboxPatch
import numpy as np

warnings.filterwarnings("ignore")

# Fix: matplotlib.path.Path.__deepcopy__ infinite recursion on Python 3.14
def _path_deepcopy(self, memo):
    cls = type(self)
    result = cls.__new__(cls)
    memo[id(self)] = result
    for k, v in self.__dict__.items():
        setattr(result, k, copy.deepcopy(v, memo))
    return result

_mpath.Path.__deepcopy__ = _path_deepcopy

# ── colour palette ─────────────────────────────────────────────────────────────
C = {
    "bg":        "#F1F5F9",   # soft slate grey page background
    "card":      "#FFFFFF",   # chart / card background
    "primary":   "#2563EB",
    "secondary": "#7C3AED",
    "accent":    "#F59E0B",
    "danger":    "#EF4444",
    "success":   "#10B981",
    "text":      "#0F172A",   # near-black for titles
    "body":      "#334155",   # slightly lighter for body text
    "muted":     "#64748B",
    "border":    "#CBD5E1",
    "header_bg": "#1E293B",   # dark slate for page header bands
}

CAT_COLORS = [
    "#2563EB", "#7C3AED", "#F59E0B", "#10B981", "#EF4444",
    "#EC4899", "#06B6D4", "#84CC16", "#F97316", "#6366F1",
    "#14B8A6", "#A855F7",
]

IMPACT_COLORS = {"High": "#EF4444", "Medium": "#F59E0B", "Low": "#10B981"}

# ── matplotlib rc ──────────────────────────────────────────────────────────────

def apply_style():
    plt.rcParams.update({
        "figure.facecolor":   C["bg"],
        "axes.facecolor":     C["card"],
        "axes.edgecolor":     C["border"],
        "axes.labelcolor":    C["body"],
        "axes.titlecolor":    C["text"],
        "axes.titlesize":     10,
        "axes.titleweight":   "bold",
        "axes.labelsize":     8.5,
        "axes.spines.top":    False,
        "axes.spines.right":  False,
        "axes.spines.left":   True,
        "axes.spines.bottom": True,
        "xtick.color":        C["muted"],
        "ytick.color":        C["muted"],
        "xtick.labelsize":    7.5,
        "ytick.labelsize":    7.5,
        "grid.color":         C["border"],
        "grid.linewidth":     0.5,
        "text.color":         C["text"],
        "font.family":        "DejaVu Sans",
        "legend.fontsize":    7.5,
        "legend.framealpha":  0.9,
        "legend.edgecolor":   C["border"],
        "patch.linewidth":    0.5,
    })


def new_figure(w=11.69, h=8.27):
    """A4 landscape figure."""
    fig = plt.figure(figsize=(w, h))
    fig.patch.set_facecolor(C["bg"])
    return fig


# ── page chrome ────────────────────────────────────────────────────────────────

def page_header_band(fig, title: str, subtitle: str = "", color: str = None):
    """
    Full-width dark band at the top of every page.
    Returns the axes so callers can add extra elements if needed.
    """
    color = color or C["header_bg"]
    ax = fig.add_axes([0, 0.934, 1.0, 0.066])
    ax.set_facecolor(color)
    ax.axis("off")
    for spine in ax.spines.values():
        spine.set_visible(False)

    ax.text(0.013, 0.52, title, transform=ax.transAxes,
            fontsize=13, fontweight="bold", color="white", va="center")
    if subtitle:
        ax.text(0.987, 0.52, subtitle, transform=ax.transAxes,
                fontsize=8.5, color="white", alpha=0.75, va="center", ha="right")
    return ax


def page_footer(fig, page_num: int, total_pages: int = 12):
    ax = fig.add_axes([0, 0, 1.0, 0.028])
    ax.set_facecolor(C["header_bg"])
    ax.axis("off")
    ax.text(0.5, 0.5, f"Page {page_num} of {total_pages}  ·  Personal Spending Report",
            transform=ax.transAxes, fontsize=7, color="white",
            alpha=0.6, ha="center", va="center")


# ── KPI stat cards ─────────────────────────────────────────────────────────────

def stat_card(ax, label: str, value: str, color: str = None, icon: str = ""):
    """Rounded-corner KPI card using FancyBboxPatch."""
    color = color or C["primary"]
    ax.axis("off")
    ax.set_xlim(0, 1); ax.set_ylim(0, 1)

    # shadow (offset patch)
    shadow = FancyBboxPatch(
        (0.04, 0.03), 0.92, 0.90,
        boxstyle="round,pad=0.04",
        facecolor="#00000018", edgecolor="none",
        transform=ax.transAxes, zorder=1,
    )
    ax.add_patch(shadow)

    # main card
    card = FancyBboxPatch(
        (0.05, 0.06), 0.90, 0.88,
        boxstyle="round,pad=0.04",
        facecolor=color, edgecolor="none",
        transform=ax.transAxes, zorder=2,
    )
    ax.add_patch(card)

    # white sheen strip at the top (glassmorphism hint)
    sheen = FancyBboxPatch(
        (0.05, 0.78), 0.90, 0.16,
        boxstyle="round,pad=0.02",
        facecolor="white", alpha=0.12, edgecolor="none",
        transform=ax.transAxes, zorder=3,
    )
    ax.add_patch(sheen)

    ax.text(0.5, 0.60, value, ha="center", va="center",
            transform=ax.transAxes,
            fontsize=15, fontweight="bold", color="white", zorder=4)
    ax.text(0.5, 0.25, label, ha="center", va="center",
            transform=ax.transAxes,
            fontsize=7.5, color="white", alpha=0.88, zorder=4)


# legacy alias used by some pages
def stat_box(ax, label, value, color=None):
    stat_card(ax, label, value, color)


# ── score arc gauge ────────────────────────────────────────────────────────────

def score_arc_gauge(ax, score_10: float, color: str):
    """
    Half-circle (180°) arc gauge.
    Arc goes left→right = 0→10, drawn as a thick ring using fill().
    """
    ax.set_xlim(-1.35, 1.35)
    ax.set_ylim(-0.25, 1.30)
    ax.axis("off")
    ax.set_facecolor("none")

    r_out, r_in = 1.00, 0.70
    N = 400
    theta_all  = np.linspace(np.pi, 0, N)   # 180° → 0°

    # ── background ring (grey) ────────────────────────────────────────────────
    xo = r_out * np.cos(theta_all)
    yo = r_out * np.sin(theta_all)
    xi = r_in  * np.cos(theta_all[::-1])
    yi = r_in  * np.sin(theta_all[::-1])
    ax.fill(np.concatenate([xo, xi]),
            np.concatenate([yo, yi]),
            color=C["border"], zorder=1, linewidth=0)

    # ── filled ring (score colour) ────────────────────────────────────────────
    n_fill = max(int(score_10 / 10 * N), 1)
    theta_f = theta_all[:n_fill]
    xof = r_out * np.cos(theta_f)
    yof = r_out * np.sin(theta_f)
    xif = r_in  * np.cos(theta_f[::-1])
    yif = r_in  * np.sin(theta_f[::-1])
    ax.fill(np.concatenate([xof, xif]),
            np.concatenate([yof, yif]),
            color=color, zorder=2, linewidth=0)

    # ── centre score text ─────────────────────────────────────────────────────
    ax.text(0, 0.22, f"{score_10:.1f}", ha="center", va="center",
            fontsize=36, fontweight="bold", color=C["text"], zorder=3)
    ax.text(0, -0.10, "out of 10", ha="center", va="center",
            fontsize=9, color=C["muted"], zorder=3)

    # ── end-stop dots ─────────────────────────────────────────────────────────
    for angle in (np.pi, 0):
        cx = ((r_out + r_in) / 2) * np.cos(angle)
        cy = ((r_out + r_in) / 2) * np.sin(angle)
        circ = plt.Circle((cx, cy), 0.048, color=C["bg"], zorder=5)
        ax.add_patch(circ)


# ── chart helpers ──────────────────────────────────────────────────────────────

def gradient_fill(ax, x, y, color: str, alpha_top=0.30, alpha_bot=0.02):
    """Gradient-alpha fill below a line using stacked fill_between slices."""
    n = 60
    y_max, y_min = max(y), min(0, min(y))
    for i in range(n):
        alpha = alpha_top * (1 - i / n) ** 1.6 + alpha_bot
        y_low  = y_min + (y_max - y_min) * (i / n)
        y_high = y_min + (y_max - y_min) * ((i + 1) / n)
        ax.fill_between(x,
                        np.clip(y, y_low, y_high),
                        y_low,
                        color=color, alpha=alpha, linewidth=0)


def add_chart_frame(ax, title: str = "", color: str = None):
    """Give an axes a white card look with a subtle top-left title label."""
    color = color or C["primary"]
    ax.set_facecolor(C["card"])
    for spine in ["top", "right"]:
        ax.spines[spine].set_visible(False)
    for spine in ["left", "bottom"]:
        ax.spines[spine].set_color(C["border"])
    if title:
        ax.set_title(title, fontweight="bold", fontsize=9.5,
                     pad=8, loc="left", color=C["text"])


# ── formatters ─────────────────────────────────────────────────────────────────

def fmt(n: float) -> str:
    if n >= 1_00_000:
        return f"Rs.{n / 1_00_000:.1f}L"
    if n >= 1_000:
        return f"Rs.{n / 1_000:.1f}K"
    return f"Rs.{n:.0f}"


def rs_formatter():
    return mticker.FuncFormatter(lambda x, _: fmt(x))


# ── score helpers ──────────────────────────────────────────────────────────────

def score_color(score_out_of_10: float) -> str:
    if score_out_of_10 >= 7.0: return C["success"]
    if score_out_of_10 >= 5.0: return C["accent"]
    return C["danger"]


def score_grade(score_100: int) -> str:
    if score_100 >= 85: return "A"
    if score_100 >= 70: return "B"
    if score_100 >= 55: return "C"
    if score_100 >= 40: return "D"
    return "F"
