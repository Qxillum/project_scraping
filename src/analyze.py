from pathlib import Path
from matplotlib.colors import LinearSegmentedColormap

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

from config import ACCENT, HEATMAP_CMAP, MOVING_AVG_COLOR, PALETTE


FIG_DIR = Path(__file__).resolve().parent.parent / "figures"

WEEK_ORDER = [
    "Monday", "Tuesday", "Wednesday", "Thursday",
    "Friday", "Saturday", "Sunday"
]

WEEK_FR = ["Lun", "Mar", "Mer", "Jeu", "Ven", "Sam", "Dim"]

sns.set_theme(style="whitegrid")


def compute_metrics(df: pd.DataFrame) -> dict:
    per_day = df.groupby("date").size()
    total = len(df)
    reverts = int(df["is_revert"].sum())
    mean_diff = df["size_diff"].mean()

    return {
        "total_edits": total,
        "unique_editors": df["user"].nunique(),
        "anon_share": round(100 * df["anon"].mean(), 1),
        "revert_count": reverts,
        "revert_rate_pct": round(100 * reverts / total, 1) if total else 0,
        "peak_day": str(per_day.idxmax()),
        "peak_value": int(per_day.max()),
        "date_start": str(df["timestamp"].min().date()),
        "date_end": str(df["timestamp"].max().date()),
        "mean_size_diff": int(mean_diff) if pd.notna(mean_diff) else 0,
    }


def plot_timeseries(df: pd.DataFrame, page: str) -> Path:
    per_day = df.groupby("date").size()

    dates = pd.date_range(
        per_day.index.min(),
        per_day.index.max(),
        freq="D"
    )

    per_day = per_day.reindex(dates.date, fill_value=0)
    moving_average = per_day.rolling(7, min_periods=1).mean()

    peak_day = per_day.idxmax()
    peak_value = int(per_day.max())

    fig, ax = plt.subplots(figsize=(12, 5))

    ax.bar(
        dates,
        per_day.values,
        color=PALETTE[2],
        alpha=0.55,
        label="Modifications par jour"
    )

    ax.plot(
        dates,
        moving_average.values,
        color=MOVING_AVG_COLOR,
        linewidth=2.4,
        label="Moyenne mobile sur 7 jours"
    )

    ax.annotate(
        f"Pic : {peak_value}\n{peak_day}",
        xy=(pd.Timestamp(peak_day), peak_value),
        xytext=(0.12, 0.85),
        textcoords="axes fraction",
        arrowprops={"arrowstyle": "->", "color": ACCENT},
        color=ACCENT
    )

    ax.set_title(f"Modifications par jour : {page}")
    ax.set_xlabel("Date")
    ax.set_ylabel("Nombre de modifications")
    ax.legend()

    fig.tight_layout()
    return _save(fig, page, "timeseries")


def plot_top_contributors(
    df: pd.DataFrame,
    page: str,
    top_n: int = 15
) -> Path:
    counts = df["user"].value_counts().head(top_n).sort_values()

    fig, ax = plt.subplots(figsize=(10, 7))

    bars = ax.barh(
        counts.index,
        counts.values,
        color=_gradient(len(counts))
    )

    for bar, value in zip(bars, counts.values):
        ax.text(
            value,
            bar.get_y() + bar.get_height() / 2,
            f" {value}",
            va="center"
        )

    ax.set_title(f"Top {top_n} contributeurs : {page}")
    ax.set_xlabel("Nombre de modifications")
    ax.set_ylabel("")

    fig.tight_layout()
    return _save(fig, page, "top_contributors")


def plot_activity_heatmap(df: pd.DataFrame, page: str) -> Path:
    activity = df.pivot_table(
        index="weekday",
        columns="hour",
        values="revid",
        aggfunc="count",
        fill_value=0
    )

    activity = activity.reindex(
        index=WEEK_ORDER,
        columns=range(24),
        fill_value=0
    )

    fig, ax = plt.subplots(figsize=(13, 5))

    sns.heatmap(
        activity,
        cmap=HEATMAP_CMAP,
        cbar_kws={"label": "Nombre de modifications"},
        ax=ax
    )

    ax.set_yticklabels(WEEK_FR, rotation=0)
    ax.set_title(f"Activité par jour et par heure : {page}")
    ax.set_xlabel("Heure UTC")
    ax.set_ylabel("Jour")

    fig.tight_layout()
    return _save(fig, page, "heatmap")


def _gradient(n: int):
    cmap = LinearSegmentedColormap.from_list("gradient", PALETTE)
    return [cmap(i / max(n - 1, 1)) for i in range(n)]


def _save(fig, page: str, name: str) -> Path:
    FIG_DIR.mkdir(parents=True, exist_ok=True)

    path = FIG_DIR / f"{page.replace(' ', '_')}_{name}.png"

    fig.savefig(path, dpi=150, bbox_inches="tight")
    plt.close(fig)

    return path


def run_all(df: pd.DataFrame, page: str) -> dict:
    return {
        "metrics": compute_metrics(df),
        "figures": {
            "timeseries": plot_timeseries(df, page),
            "top_contributors": plot_top_contributors(df, page),
            "heatmap": plot_activity_heatmap(df, page),
        },
    }