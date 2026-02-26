from __future__ import annotations

import argparse
import json
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List

import pandas as pd
import yaml
from tqdm import tqdm

from providers import get_provider
from providers.base import GenParams
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


def load_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def render_prompt(template: str, inp: str) -> str:
    return template.format(input=inp)


def now_stamp() -> str:
    return datetime.now().strftime("%Y-%m-%d_%H%M%S")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", default="eval/data/examples.jsonl")
    ap.add_argument("--runs", default="eval/runs.yaml")
    ap.add_argument("--outdir", default="eval/results")
    ap.add_argument("--bertscore_min", type=float, default=0.85, help="Guardrail threshold for meaning preservation")
    args = ap.parse_args()

    data_path = Path(args.data)
    runs_path = Path(args.runs)
    out_root = Path(args.outdir)

    examples = load_jsonl(data_path)

    runs_cfg = yaml.safe_load(runs_path.read_text(encoding="utf-8"))
    runs = runs_cfg.get("runs", [])
    if not runs:
        raise RuntimeError("No runs found in runs.yaml under key: runs")

    simplify_tpl = load_text(Path("eval/prompts/simplify.txt"))
    soften_tpl = load_text(Path("eval/prompts/soften.txt"))

    run_dir = out_root / now_stamp()
    run_dir.mkdir(parents=True, exist_ok=True)

    raw_path = run_dir / "raw_outputs.jsonl"
    metrics_path = run_dir / "metrics.csv"

    # Provider instances (reuse across runs)
    providers: Dict[str, Any] = {}

    raw_f = raw_path.open("w", encoding="utf-8")
    metric_rows: List[Dict[str, Any]] = []

    # Warn once if Detoxify isn't installed (soften toxicity)
    try:
        import detoxify  # noqa: F401
    except Exception:
        print("[warn] detoxify not installed -> toxicity metrics will be NaN. (Optional) pip install detoxify torch")

    for run in runs:
        run_name = run["name"]
        provider_name = run["provider"]
        model = run["model"]
        temperature = float(run.get("temperature", 0.2))
        max_tokens = int(run.get("max_tokens", 512))
        top_p = run.get("top_p", None)
        params = GenParams(temperature=temperature, max_tokens=max_tokens, top_p=top_p)

        if provider_name not in providers:
            providers[provider_name] = get_provider(provider_name)
        provider = providers[provider_name]

        for ex in tqdm(examples, desc=f"run={run_name}", unit="ex"):
            ex_id = ex["id"]
            task = ex["task"]
            inp = ex["input"]

            if task not in ("simplify", "soften"):
                continue

            tpl = simplify_tpl if task == "simplify" else soften_tpl
            prompt = render_prompt(tpl, inp)

            # Generate
            try:
                out = provider.generate(model=model, prompt=prompt, params=params)
            except Exception as e:
                out = ""
                err = repr(e)
            else:
                err = ""

            raw_record = {
                "run": run_name,
                "provider": provider_name,
                "model": model,
                "task": task,
                "id": ex_id,
                "input": inp,
                "output": out,
                "error": err,
                "temperature": temperature,
                "max_tokens": max_tokens,
                "top_p": top_p,
            }
            raw_f.write(json.dumps(raw_record, ensure_ascii=False) + "\n")

            # Metrics
            row: Dict[str, Any] = {
                "run": run_name,
                "provider": provider_name,
                "model": model,
                "task": task,
                "id": ex_id,
                "error": err,
                "input_len": len(inp),
                "output_len": len(out),
            }

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

    raw_f.close()

    df = pd.DataFrame(metric_rows)
    df.to_csv(metrics_path, index=False)

    # Summary (per run/task)
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
    summary_path = run_dir / "summary.csv"
    summary.to_csv(summary_path, index=False)

    print(f"\nWrote:\n- {raw_path}\n- {metrics_path}\n- {summary_path}")


if __name__ == "__main__":
    main()