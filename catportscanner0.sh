#!/usr/bin/env bash
#
# Meowmow SDK 1.0 — Authorized Port Scanner
# Author: Cat A I (Meowmow SDK)
#
# Purpose:
#   Educational / defensive TCP port scanning.
#   Scan ONLY hosts you own or have explicit permission to test.
#
# Usage:
#   ./meowmow_portscan.sh <host> <start_port> <end_port> [timeout_ms]
#
# Example:
#   ./meowmow_portscan.sh 127.0.0.1 1 1024 300
#

set -euo pipefail

# ─────────────────────────────────────────────
# ARG PARSE
# ─────────────────────────────────────────────
HOST="${1:-}"
START_PORT="${2:-}"
END_PORT="${3:-}"
TIMEOUT_MS="${4:-300}"

if [[ -z "$HOST" || -z "$START_PORT" || -z "$END_PORT" ]]; then
  echo "Usage: $0 <host> <start_port> <end_port> [timeout_ms]"
  exit 1
fi

if ! command -v nc >/dev/null 2>&1; then
  echo "Error: 'nc' (netcat) is required."
  exit 1
fi

if ! [[ "$START_PORT" =~ ^[0-9]+$ && "$END_PORT" =~ ^[0-9]+$ ]]; then
  echo "Error: ports must be integers."
  exit 1
fi

if (( START_PORT < 1 || END_PORT > 65535 || START_PORT > END_PORT )); then
  echo "Error: invalid port range."
  exit 1
fi

# ─────────────────────────────────────────────
# BANNER
# ─────────────────────────────────────────────
cat <<'BANNER'
🐾 Meowmow SDK 1.0 — Authorized Port Scanner
───────────────────────────────────────────
Mode : DEFENSIVE / LAB
Method: TCP connect scan (nc)
BANNER

echo "Target  : $HOST"
echo "Ports   : $START_PORT-$END_PORT"
echo "Timeout : ${TIMEOUT_MS}ms"
echo "───────────────────────────────────────────"

# ─────────────────────────────────────────────
# SCAN LOOP
# ─────────────────────────────────────────────
OPEN_COUNT=0
CLOSED_COUNT=0

for ((port=START_PORT; port<=END_PORT; port++)); do
  # -z : zero-I/O mode (connect only)
  # -w : timeout (seconds, fractional ok)
  if nc -z -w "$(awk "BEGIN{print $TIMEOUT_MS/1000}")" "$HOST" "$port" 2>/dev/null; then
    printf "[OPEN ] %s:%d\n" "$HOST" "$port"
    ((OPEN_COUNT++))
  else
    ((CLOSED_COUNT++))
  fi
done

# ─────────────────────────────────────────────
# SUMMARY
# ─────────────────────────────────────────────
echo "───────────────────────────────────────────"
echo "Scan complete."
echo "Open ports  : $OPEN_COUNT"
echo "Closed/Filtered : $CLOSED_COUNT"
echo "───────────────────────────────────────────"
