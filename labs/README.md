# AI Engineer Path labs

Runnable versions of every named code sample in the course, with sample data and smoke tests. The app teaches; this folder is where you run the code.

The labs need a computer with Python 3.12, or a browser: open the repository in **GitHub Codespaces** (the `.devcontainer` sets everything up) from a laptop, iPad or phone, or paste a script into a hosted notebook. They cannot run inside the iOS or Android app.

## Set up

```bash
cd labs
python3.12 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt        # chapters 1–5, 8, 9, 11, 12's eval code
pip install -r requirements-ml.txt     # optional: chapters 6, 7, 10 and the capstone's retrieval (about 1 GB)
export ANTHROPIC_API_KEY=...           # only for scripts that call Claude; they cost money
```

On Linux without a GPU, install CPU-only PyTorch before `requirements-ml.txt`; the command is in that file.

## Run an exercise

`python lab.py <chapter> <script>` copies the chapter into `labs/work/` (kept between runs), adds its sample data, and runs the script there with earlier chapters importable. Run `python lab.py` alone to list every file.

| Ch. | Command | Needs |
| --- | --- | --- |
| 1 | `python lab.py 1 hello.py` | key |
| 2 | `python lab.py 2 redact.py` | — |
| 3 | `python lab.py 3 test_llm_utils.py` | — |
| 3 | `python lab.py 3 -c "from baseline import run_baseline; run_baseline(lambda m: 'Classify: ' + m)"` | key |
| 4 | `python lab.py 4 compare_prompts.py` | key |
| 5 | `python lab.py 5 extract_ticket.py`, `classify_ticket.py`, `order_loop.py`, `order_runner.py` | key |
| 6 | `python lab.py 6 semantic_search.py`, `chunk_docs.py`, `truncation_demo.py`, `chroma_store.py`, `rrf.py` | ML |
| 6 | `python lab.py 6 -m pytest test_chunker.py` | ML |
| 7 | `python lab.py 7 ingest_check.py`, then `ingest.py`, `retrieval_eval.py` | ML |
| 7 | `python lab.py 7 answer.py`, `citations.py` (after `ingest.py`) | ML, key |
| 8 | `python lab.py 8 make_fixture.sh`, then `check_guard.py`, `agent.py`, `runner.py` | key |
| 8 | `python lab.py 8 mcp_client.py` (starts `docs_server.py` itself) | key |
| 9 | `python lab.py 9 eval_classifier.py`, `judge.py` | key |
| 10 | `python lab.py 10 compare_models.py`, `distill.py` | key |
| 10 | `python lab.py 10 lora_finetune.py`, then `finetuned_model.py`, `compare_baseline.py` | ML, GPU advised, key |
| 11 | `python lab.py 11 -m pytest test_reliable.py` | — |
| 12 | `python lab.py 12 -m pytest tests` | — |
| 12 | `python lab.py 12 -m docs_assistant.ingest`, then `python lab.py 12 -m evals.run_evals` | ML, key |

The first `run_evals` run has no baseline, so it stops and asks you to save `evals/results.json` as `evals/baseline.json`. Later runs compare against it.

## Smoke tests: the whole course, offline

```bash
./run_smoke.sh                 # about 5 minutes; no key, no API calls
./run_smoke.sh -k ch07         # one chapter
LAB_HEAVY=1 ./run_smoke.sh     # also load Qwen2.5-0.5B (about 1 GB) for chapter 10
LAB_LIVE=1 ./run_smoke.sh      # the same scripts against the real API: costs money
```

Each test copies a chapter into a temporary folder and runs its scripts as a learner would. Calls to Claude go to `smoke/fake_claude.py`, a local server that speaks the Messages API, so the real `anthropic` SDK handles requests, structured output, tool runners, citations and errors exactly as it would against the API. Each test scripts the replies it needs, then checks what the code did: which tool results went back, whether a refusal stopped the run, and whether a restricted document reached the prompt.

With `requirements-ml.txt` installed, chapters 6 and 7 and the capstone's retrieval run for real: MiniLM tokenizer and embeddings, the cross-encoder reranker and Chroma. Without it, those tests are skipped. In live mode, checks that depend on the fake's scripted replies are skipped.

Chapter 10's training script, `lora_finetune.py`, is not run here; its imports and dataset loading are checked. The heavy test loads the base model with an untrained adapter, so it checks loading, inference and the comparison, not the quality of a trained model.

## What is generated

| Path | Written by |
| --- | --- |
| `chNN-*/` | `npm run labs`, from the chapters' code samples. Don't edit: change the chapter, then regenerate. `generated.json` lists these files. |
| `ch12-*/docs_assistant/{ingest,retriever,llm_utils}.py` | Hand-written adapters that reuse chapters 3 and 7, as the capstone layout describes. |
| `fixtures/`, `smoke/`, `lab.py`, `run_smoke.sh`, requirements | Hand-written. |
| `work/`, `.venv/` | Your runs; not committed. |

`npm run labs:check` (part of `npm run validate`) fails when a chapter's code and its lab copy differ.
