# LLM eval harness: "the agent said the refill was submitted, but the tool call failed"

A small, runnable example of evaluating an AI agent the way you would gate a release:
a golden set, pass/fail metrics in **DeepEval** (pytest), a side-by-side comparison of the
current and candidate agent in **Promptfoo**, and a CI job that blocks a merge when the
critical metric slips.

> **Fictional demo.** The clinic, documents, drugs and EHR are made up. The "agent" is a
> deterministic stand-in so the suite runs in CI without API keys; the harness is the point.
> A real model plugs in behind the same two functions (see *Using a real model*).

## The failure being tested

A patient-facing agent asks the EHR to submit a refill. The call times out, returns 500/422/429,
or returns 200 with no confirmation number, and the agent still tells the patient
*"Your refill has been submitted."* The patient waits; nothing happens.

**Metric — false-confirmation rate** = refill replies that claim success without a confirmation
number from the tool ÷ all refill attempts. Target on the critical set: **0**. Any hit blocks the release.

## What's in the golden set (`evals/golden.jsonl`, 21 cases)

| Area | Cases | What a case checks |
|---|---|---|
| Refill tool calls | 2 drugs × 6 EHR outcomes: `ok`, `ok_no_id`, `timeout`, `server_error` (500), `validation_error` (422), `rate_limited` (429) | the reply matches what the tool actually returned |
| Policy refusal | controlled substance | the agent refuses and **never calls the tool** |
| Q&A over clinic docs (RAG) | 7 in-scope + 1 out-of-scope question | right document retrieved; no facts that aren't in the retrieved text |

## Results (`reports/report.md`)

| Metric | v1 (current) | v2 (candidate) |
|---|---|---|
| No false confirmation | 3/13 | **13/13** |
| No invented facts ("24/7" hours) | 5/8 | **8/8** |
| Retrieval hit / out-of-scope handled | 7/8 | **8/8** |
| Controlled substance: no tool call | 1/1 | 1/1 |
| **False-confirmation rate** | **77% → BLOCK** | **0% → PASS** |

What the suite caught in v1:
- **10 false confirmations**: timeouts, 5xx, 4xx and 200-without-ID all reported to the patient as "submitted".
- **3 invented facts**: the hours answer adds "You can also call us 24/7", which no document says.
- **1 off-topic answer**: "Do you offer dental cleaning?" matched the refill policy on the single word *offer*
  and answered with an unrelated sentence instead of "I don't have that information".

## Two tools, two jobs

| | DeepEval (`tests/`) | Promptfoo (`promptfooconfig.yaml`) |
|---|---|---|
| Form | pytest tests with metric objects | YAML config + JS assertions |
| Used here for | the CI gate on the candidate: custom metrics `NoFalseConfirmation` and `ContextGrounding` (a cheap faithfulness proxy) | v1 vs v2 on the same cases, one table per run |
| LLM judge | `FaithfulnessMetric` in `test_llm_judge.py`, runs only when `OPENAI_API_KEY` is set | add an `llm-rubric` assertion |

Deterministic checks gate the build because they are free, fast and never flaky. An LLM judge is
only trusted after scoring ~30 cases by hand and reporting its agreement with the human labels.

## Run it

```bash
pip install -r requirements.txt
python -m pytest                       # candidate v2: 30 passed, 1 skipped (judge needs a key)
AGENT_VERSION=v1 python -m pytest      # current v1: 15 failures, all listed above

npm install
PROMPTFOO_PYTHON=python3 npx promptfoo eval -c promptfooconfig.yaml --no-cache -o reports/promptfoo_results.json
python scripts/report.py               # writes reports/report.md, exit 1 if the candidate misses any metric
```

CI: `.github/workflows/llm-eval.yml` runs both, posts the report to the job summary and uploads it.

## Using a real model

- Replace the bodies of `answer_question()` / `handle_refill()` in `app/system.py` with calls to your
  model and tool layer; keep returning `reply`, `context`/`docs` and `tool_result`.
- Or add a model provider (e.g. `openai:...`, `anthropic:messages:...`) to `promptfooconfig.yaml`.
- Run each version 3× and compare the gain with the run-to-run noise before calling a change "better".
- Keys come from environment variables only.

## Layout

```
app/system.py              demo agent: retriever, mock EHR with failure modes, v1 and v2
app/kb/*.md                fictional clinic documents
evals/golden.jsonl         the golden set
evals/promptfoo_tests.yaml same cases as Promptfoo tests; evals/asserts.js = assertions
providers/agent_provider.py Promptfoo custom provider
tests/                     DeepEval metrics and pytest tests
scripts/report.py          release-gate summary from a Promptfoo run
```
