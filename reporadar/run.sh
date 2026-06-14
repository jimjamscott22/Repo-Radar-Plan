#!/usr/bin/env bash
# Launch RepoRadar from its virtual environment.
set -euo pipefail
cd "$(dirname "$0")"
if [ -d ".venv" ]; then
    source .venv/bin/activate
fi
exec python -m reporadar.app
