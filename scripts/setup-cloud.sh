#!/usr/bin/env bash
# Installs development tools on the cloud machine, never on the user's computer.
set -euo pipefail
cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.."
if [[ "${1:-}" != "" && "${1:-}" != "--browser-deps" ]]; then
  echo 'Usage: bash scripts/setup-cloud.sh [--browser-deps]' >&2
  exit 2
fi
if [[ ! -x .venv/bin/python ]]; then
  python3 -m venv .venv
fi
.venv/bin/python -m pip install --disable-pip-version-check -r requirements-dev.txt
export PLAYWRIGHT_BROWSERS_PATH="$PWD/.cache/ms-playwright"
if [[ -n "${KALKPILOT_CHROMIUM:-}" ]]; then
  test -x "$KALKPILOT_CHROMIUM"
elif command -v chromium >/dev/null 2>&1; then
  echo 'Using installed Chromium for browser tests.'
elif [[ "${1:-}" == "--browser-deps" ]]; then
  .venv/bin/python -m playwright install --with-deps chromium
else
  .venv/bin/python -m playwright install chromium
fi
echo 'Cloud setup complete. Start: python3 scripts/dev.py; test: bash scripts/test-cloud.sh'
