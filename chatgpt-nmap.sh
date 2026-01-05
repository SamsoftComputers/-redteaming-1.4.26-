#!/usr/bin/env bash
# ============================================================
# nmap_toolkit.sh — Practical Nmap Wrapper (Single-File Script)
# Author: ChatGPT & Mr. Samsoft
# Purpose: Authorized network scanning & inventory
# ============================================================

set -euo pipefail

# ---------------------------
# Defaults
# ---------------------------
TARGET=""
OUTDIR="nmap_results"
PROFILE="quick"
EXTRA_ARGS=""
TIMESTAMP="$(date +%Y%m%d_%H%M%S)"

# ---------------------------
# Usage
# ---------------------------
usage() {
  cat <<'EOF'
Usage:
  ./nmap_toolkit.sh -t <target> [-p <profile>] [-o <outdir>] [-x "<extra nmap args>"]

Targets:
  IP, CIDR, hostname, or file (e.g. targets.txt)

Profiles:
  quick      - Fast scan of top ports + version detect
  full       - Full TCP scan (1-65535) + version detect
  udp        - Common UDP ports
  discovery  - Host discovery only (ping sweep)

Examples:
  ./nmap_toolkit.sh -t 192.168.1.0/24
  ./nmap_toolkit.sh -t example.com -p full
  ./nmap_toolkit.sh -t targets.txt -p udp -x "--reason"

NOTE:
  Use ONLY on networks you own or have explicit permission to test.
EOF
  exit 1
}

# ---------------------------
# Parse args
# ---------------------------
while getopts ":t:p:o:x:h" opt; do
  case $opt in
    t) TARGET="$OPTARG" ;;
    p) PROFILE="$OPTARG" ;;
    o) OUTDIR="$OPTARG" ;;
    x) EXTRA_ARGS="$OPTARG" ;;
    h|*) usage ;;
  esac
done

[[ -z "$TARGET" ]] && usage

mkdir -p "$OUTDIR"

OUTBASE="$OUTDIR/nmap_${PROFILE}_${TIMESTAMP}"

# ---------------------------
# Scan profiles
# ---------------------------
case "$PROFILE" in
  quick)
    CMD="nmap -T4 -F -sV --open"
    ;;
  full)
    CMD="nmap -T4 -p- -sV --open"
    ;;
  udp)
    CMD="nmap -T4 -sU --top-ports 100"
    ;;
  discovery)
    CMD="nmap -sn"
    ;;
  *)
    echo "[!] Unknown profile: $PROFILE"
    exit 1
    ;;
esac

# ---------------------------
# Target handling
# ---------------------------
if [[ -f "$TARGET" ]]; then
  TARGET_ARG="-iL $TARGET"
else
  TARGET_ARG="$TARGET"
fi

# ---------------------------
# Execute scan
# ---------------------------
echo "[*] Author        : ChatGPT & Mr. Samsoft"
echo "[*] Target        : $TARGET"
echo "[*] Profile       : $PROFILE"
echo "[*] Output prefix : $OUTBASE"
echo "[*] Extra args    : ${EXTRA_ARGS:-none}"
echo "[*] Starting scan…"
echo

$CMD $TARGET_ARG $EXTRA_ARGS \
  -oA "$OUTBASE"

echo
echo "[✓] Scan complete"
echo "[✓] Results saved as:"
echo "    $OUTBASE.nmap"
echo "    $OUTBASE.gnmap"
echo "    $OUTBASE.xml"
