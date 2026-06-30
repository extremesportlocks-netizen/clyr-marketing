#!/bin/bash
# Draft one journal article when X API allows. Safe for cron/launchd (hourly).
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
LOG="$ROOT/scripts/x-articles/drip.log"
cd "$ROOT"
echo "=== $(date -u +%Y-%m-%dT%H:%M:%SZ) ===" >> "$LOG"
python3 scripts/x-journal-syndicate.py drip --tier ashersoil >> "$LOG" 2>&1 && ec=0 || ec=$?
if [[ "$ec" -eq 2 ]]; then
  echo "rate limited, will retry next hour" >> "$LOG"
  exit 0
fi
exit "$ec"