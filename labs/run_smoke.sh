#!/usr/bin/env bash
# Runs every offline smoke test: the chapters' own code against a local fake Claude
# server, so no API key is needed. Embedding and RAG tests run for real when
# requirements-ml.txt is installed (first run downloads about 200 MB of models).
#   ./run_smoke.sh                 everything that can run here
#   ./run_smoke.sh -k ch07         one chapter
#   LAB_HEAVY=1 ./run_smoke.sh     also load Qwen2.5-0.5B for chapter 10 (about 1 GB)
#   LAB_LIVE=1 ./run_smoke.sh      use the real API with ANTHROPIC_API_KEY (costs money)
set -euo pipefail
cd "$(dirname "$0")"
PYTHON=${PYTHON:-$( [ -x .venv/bin/python ] && echo .venv/bin/python || echo python3 )}
exec "$PYTHON" -m pytest -q -p no:cacheprovider smoke "$@"
