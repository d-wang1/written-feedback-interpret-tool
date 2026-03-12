from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Dict, Any, List

import pandas as pd

from metrics import (
    bertscore_f1,
    simplify_metrics,
    simplify_composite,
    soften_metrics,
    soften_composite,
)


def load_jsonl(path: Path) -> List[Dict[str, Any]]:
    rows = []
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--raw", required=True, help="Path to raw_outputs.jsonl")
    ap.add_argument("--outdir", default=None, help="Output directory for metrics.csv and summary.csv")
    ap.add_argument("--bertscore_min", type=float, default=0.85)
    args = ap.parse_args()

    raw_path = Path(args.raw)
    outdir = Path(args.outdir) if args.outdir else raw_path.parent
    outdir.mkdir(parents=True, exist_ok=True)

    raw_rows = load_jsonl(raw_path)
    metric_rows = []

    try:
        import detoxify  # noqa: F401
    except Exception:
        print("[warn] detoxify not installed -> toxicity metrics may be NaN")

    for rec in raw_rows:
        run = rec["run"]
        provider = rec["provider"]
        model = rec["model"]
        task = rec["task"]
        ex_id = rec["id"]
        inp = rec["input"]
        out = rec.get("output", "")
        err = rec.get("error", "")

        row: Dict[str, Any] = {
            "run": run,
            "provider": provider,
            "model": model,
            "task": task,
            "id": ex_id,
            "error": err,
            "input_len": len(inp),
            "output_len": len(out),
        }

        if task not in ("simplify", "soften"):
            continue

        if not out.strip() or err:
            row.update(
                {
                    "bertscore_f1": float("nan"),
                    "passes_semantic": False,
                    "composite": float("nan"),
                }
            )
            metric_rows.append(row)
            continue

        bs = bertscore_f1(inp, out)
        row["bertscore_f1"] = bs
        row["passes_semantic"] = bool(bs >= args.bertscore_min)

        if task == "simplify":
            sm = simplify_metrics(inp, out)
            row.update(sm)
            row["composite"] = simplify_composite(row) if row["passes_semantic"] else float("nan")
        else:
            tm = soften_metrics(inp, out)
            row.update(tm)
            row["composite"] = soften_composite(row) if row["passes_semantic"] else float("nan")

        metric_rows.append(row)

    df = pd.DataFrame(metric_rows)

    metrics_path = outdir / "metrics.csv"
    summary_path = outdir / "summary.csv"

    df.to_csv(metrics_path, index=False)

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
    summary.to_csv(summary_path, index=False)

    print(f"Wrote:\n- {metrics_path}\n- {summary_path}")


if __name__ == "__main__":
    main()