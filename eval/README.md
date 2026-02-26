Perfect — since you're using **Groq only (for now)** and **Python 3.11.9**, I'll tailor this specifically to your current setup and make it clean, professional, and GitHub-ready.

You can copy-paste the following directly into:

```
eval/README.md
```

---

# Evaluation Pipeline

### Written Feedback Interpretation Tool

---

## Overview

This evaluation pipeline measures the performance of large language models (LLMs) on two core tasks:

* **Language Simplification** — rewriting complex academic feedback to be clearer and easier to understand.
* **Tone Softening** — rewriting blunt or harsh feedback to be more constructive and supportive.

The system enables:

* Structured comparison of multiple model configurations
* Reproducible evaluation across prompt variations
* Quantitative measurement of output quality
* Leaderboard-style summaries for model selection

Currently supported provider:

* **Groq**

Recommended Python version:

* **Python 3.11.9**

---

# Setup

## 1. Create a Python 3.11.9 virtual environment

```bash
python -m venv .venv
source .venv/bin/activate  # Mac/Linux
# or
.\.venv\Scripts\activate   # Windows
```

## 2. Install dependencies

```bash
pip install -r requirements.txt
```

## 3. Set Groq API Key

```bash
export GROQ_API_KEY="your_api_key_here"   # Mac/Linux
# or
setx GROQ_API_KEY "your_api_key_here"     # Windows (PowerShell: $env:GROQ_API_KEY="...")
```

---

# How to Run the Evaluation

From the project root:

```bash
python eval/run_eval.py \
  --data eval/data/examples.jsonl \
  --runs eval/runs.yaml
```

To plot the summary:
```bash
python .\plot_summary.py --summary .\eval\results\<timestamp>\summary.csv --outdir .\eval\results\<timestamp>\plots
```

If arguments are omitted, defaults are used:

* `--data`: `eval/data/examples.jsonl`
* `--runs`: `eval/runs.yaml`

---

# How the Pipeline Works

For each model configuration defined in `runs.yaml`:

1. Load examples from `examples.jsonl`
2. Select the correct task prompt template
3. Insert `{input}` into the prompt
4. Send prompt to the model via Groq
5. Compute evaluation metrics
6. Save outputs and aggregated results

This repeats for every `(run, example)` pair.

---

# Defining the Evaluation Dataset

The dataset must be a **JSONL file** (`.jsonl`), where each line is a valid JSON object.

Example:

```json
{"id":"simp_001","task":"simplify","input":"Your submission demonstrates partial conceptual alignment..."}
{"id":"soft_001","task":"soften","input":"This is hard to read. You need to rewrite it."}
```

Required fields:

* `id` — unique identifier
* `task` — either `"simplify"` or `"soften"`
* `input` — original feedback text

### Important

* One JSON object per line
* No blank lines
* No trailing commas
* Must be valid JSON

---

# Prompt Templates

Prompt templates are stored as plain text files:

```
eval/prompts/simplify.txt
eval/prompts/soften.txt
```

Each template must include `{input}`.

Example:

```txt
Rewrite the following text to be simpler and clearer while preserving meaning.
Return only the rewritten text.

TEXT:
{input}
```

To change evaluation prompts, edit these files.

---

# Configuring Models

Models are defined in:

```
eval/runs.yaml
```

Example configuration:

```yaml
runs:
  - name: groq_llama31_8b_t00
    provider: groq
    model: llama-3.1-8b-instant
    temperature: 0.0
    max_tokens: 512
```

Each entry defines one experimental condition.

You can vary:

* Model name
* Temperature
* Max tokens

The pipeline will automatically compare all runs.

---

# Metrics

All metrics are computed locally.
No external LLM is used for scoring.

---

## Simplification Metrics

* Flesch Reading Ease
* Flesch–Kincaid Grade Level
* Average word length reduction
* Length ratio
* BERTScore (semantic similarity)
* Composite simplification score

---

## Tone Softening Metrics

* VADER sentiment score
* Detoxify toxicity score
* Politeness marker gain
* Profanity reduction
* Length ratio
* BERTScore
* Composite softening score

---

# Output Files

After execution, results are saved in:

```
eval/results/<timestamp>/
```

### `raw_outputs.jsonl`

Contains model outputs for every `(run, example)` pair.

### `metrics.csv`

One row per `(run, example)` with all metric values.

### `summary.csv`

Aggregated results grouped by `(task, run)`.

This functions as a model comparison leaderboard.

---

# Interpreting Results

### Simplification

Prefer runs with:

* Improved readability
* Lower grade level
* High BERTScore (meaning preserved)
* Reasonable length ratio

### Tone Softening

Prefer runs with:

* Reduced toxicity
* More positive sentiment
* High BERTScore
* Controlled output length

Trade-offs should be considered (e.g., extreme shortening may reduce clarity).

---

# Extending the Pipeline

To add a new task:

1. Create a new prompt template
2. Implement task-specific metrics in `eval/metrics/`
3. Update task logic in `run_eval.py`
4. Add dataset examples with the new task value

The architecture is modular and designed for extensibility.

