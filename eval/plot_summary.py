# plot_summary.py
from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd
import matplotlib.pyplot as plt


def plot_metric_per_task(
    df: pd.DataFrame,
    metric: str,
    outdir: Path,
    sort_desc: bool = True,
    title_prefix: str = "",
) -> None:
    if metric not in df.columns:
        print(f"[skip] '{metric}' not found in summary.csv columns: {list(df.columns)}")
        return

    outdir.mkdir(parents=True, exist_ok=True)

    # Ensure task exists; if not, treat whole file as one task
    tasks = df["task"].unique().tolist() if "task" in df.columns else ["all"]
    for task in tasks:
        sub = df if task == "all" else df[df["task"] == task].copy()
        if sub.empty:
            continue

        # Prefer "run" label; fallback to "model"
        label_col = "run" if "run" in sub.columns else ("model" if "model" in sub.columns else None)
        if label_col is None:
            raise ValueError("summary.csv must have either a 'run' or 'model' column to label bars.")

        # Sort (NaNs to bottom)
        sub["_sort_key"] = sub[metric].fillna(float("-inf") if sort_desc else float("inf"))
        sub = sub.sort_values("_sort_key", ascending=not sort_desc).drop(columns=["_sort_key"])

        # Build plot
        fig, ax = plt.subplots(figsize=(max(8, 0.6 * len(sub)), 4.8))
        ax.bar(sub[label_col].astype(str), sub[metric])

        t = f"{title_prefix}{task} — {metric}"
        ax.set_title(t)
        ax.set_xlabel(label_col)
        ax.set_ylabel(metric)
        ax.tick_params(axis="x", rotation=30, labelsize=9)

        # Annotate bars lightly
        for i, v in enumerate(sub[metric].tolist()):
            if pd.isna(v):
                continue
            ax.text(i, v, f"{v:.3f}" if isinstance(v, float) else str(v), ha="center", va="bottom", fontsize=8)

        fig.tight_layout()

        outpath = outdir / f"{task}_{metric}.png"
        fig.savefig(outpath, dpi=200)
        print(f"[saved] {outpath}")

        plt.show()
        plt.close(fig)


def main() -> None:
    ap = argparse.ArgumentParser()

    base_dir = Path(__file__).resolve().parent  # eval/

    ap.add_argument(
        "--summary",
        type=str,
        default=str(base_dir / "results" / "latest" / "summary.csv"),
        help="Path to summary.csv",
    )

    ap.add_argument(
        "--outdir",
        type=str,
        default=str(base_dir / "results" / "latest" / "plots"),
        help="Directory to save plots",
    )

    args = ap.parse_args()

    summary_path = Path(args.summary)
    outdir = Path(args.outdir)

    df = pd.read_csv(summary_path)

    # Standard metrics your summary.csv typically includes
    plot_metric_per_task(df, "composite_mean", outdir, sort_desc=True, title_prefix="Eval Summary: ")
    plot_metric_per_task(df, "bertscore_mean", outdir, sort_desc=True, title_prefix="Eval Summary: ")
    plot_metric_per_task(df, "semantic_pass_rate", outdir, sort_desc=True, title_prefix="Eval Summary: ")
    plot_metric_per_task(df, "n", outdir, sort_desc=True, title_prefix="Eval Summary: ")


if __name__ == "__main__":
    main()