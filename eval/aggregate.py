from __future__ import annotations

import argparse
from pathlib import Path
import pandas as pd


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--run_dir", required=True, help="Path like eval/results/2026-02-22_120000")
    args = ap.parse_args()

    run_dir = Path(args.run_dir)
    metrics_path = run_dir / "metrics.csv"
    if not metrics_path.exists():
        raise FileNotFoundError(metrics_path)

    df = pd.read_csv(metrics_path)

    summary = (
        df.groupby(["task", "run", "provider", "model"], dropna=False)
        .agg(
            n=("id", "count"),
            semantic_pass_rate=("passes_semantic", "mean"),
            composite_mean=("composite", "mean"),
            composite_std=("composite", "std"),
            bertscore_mean=("bertscore_f1", "mean"),
        )
        .reset_index()
        .sort_values(["task", "composite_mean"], ascending=[True, False])
    )

    out = run_dir / "summary.csv"
    summary.to_csv(out, index=False)
    print(f"Wrote {out}")

    # helpful debug: worst semantic failures
    worst = df[df["bertscore_f1"].notna()].sort_values("bertscore_f1").head(10)
    worst_out = run_dir / "worst_semantic.csv"
    worst.to_csv(worst_out, index=False)
    print(f"Wrote {worst_out}")


if __name__ == "__main__":
    main()