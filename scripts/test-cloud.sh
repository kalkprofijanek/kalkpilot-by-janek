#!/usr/bin/env bash
set -euo pipefail
cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.."
export PLAYWRIGHT_BROWSERS_PATH="$PWD/.cache/ms-playwright"
if [[ -z "${KALKPILOT_CHROMIUM:-}" ]] && command -v chromium >/dev/null 2>&1; then
  export KALKPILOT_CHROMIUM="$(command -v chromium)"
fi
if [[ -x .venv/bin/python ]]; then
  exec .venv/bin/python -m unittest discover -s tests -v
fi
exec python3 -m unittest discover -s tests -v
