#!/usr/bin/env bash
# ─────────────────────────────────────────────
# MiniShark — Wireshark-like Shell Analyzer
# Author: ChatGPT (Educational Use)
# Purpose: Read-only packet inspection
# Requires: tcpdump, awk, sed
# ─────────────────────────────────────────────

set -e

# ─── Colors ──────────────────────────────────
RED="\033[31m"
GREEN="\033[32m"
YELLOW="\033[33m"
BLUE="\033[34m"
CYAN="\033[36m"
RESET="\033[0m"

# ─── Banner ──────────────────────────────────
echo -e "${CYAN}"
echo "╔══════════════════════════════════════╗"
echo "║        MiniShark Packet Analyzer     ║"
echo "║        (Wireshark-style CLI)          ║"
echo "╚══════════════════════════════════════╝"
echo -e "${RESET}"

# ─── Dependency Check ────────────────────────
command -v tcpdump >/dev/null || {
  echo "tcpdump not found"
  exit 1
}

# ─── Usage ───────────────────────────────────
usage() {
  echo "Usage:"
  echo "  Live capture:"
  echo "    sudo ./minishark.sh live <iface> [filter]"
  echo
  echo "  Offline analysis:"
  echo "    ./minishark.sh file <pcap> [filter]"
  echo
  echo "Filters (optional):"
  echo "  tcp | udp | icmp | arp"
  echo "  port <num>"
  echo "  host <ip>"
  exit 1
}

[[ $# -lt 2 ]] && usage

MODE="$1"
TARGET="$2"
shift 2

FILTER="$*"

# ─── Build tcpdump filter ────────────────────
build_filter() {
  case "$FILTER" in
    tcp|udp|icmp|arp)
      echo "$FILTER"
      ;;
    port*)
      echo "$FILTER"
      ;;
    host*)
      echo "$FILTER"
      ;;
    *)
      echo ""
      ;;
  esac
}

TCPDUMP_FILTER=$(build_filter)

# ─── Pretty Printer ──────────────────────────
pretty_print() {
  awk '
  {
    if ($0 ~ /IP/)    { printf "\033[32m%s\033[0m\n", $0 }
    else if ($0 ~ /ARP/)  { printf "\033[33m%s\033[0m\n", $0 }
    else if ($0 ~ /ICMP/) { printf "\033[34m%s\033[0m\n", $0 }
    else print
  }'
}

# ─── Live Capture ────────────────────────────
if [[ "$MODE" == "live" ]]; then
  echo -e "${YELLOW}[+] Live capture on interface: $TARGET${RESET}"
  echo -e "${BLUE}[i] Press Ctrl+C to stop${RESET}"
  echo

  sudo tcpdump -i "$TARGET" -nn -vv $TCPDUMP_FILTER | pretty_print
fi

# ─── File Analysis ───────────────────────────
if [[ "$MODE" == "file" ]]; then
  [[ ! -f "$TARGET" ]] && {
    echo "PCAP file not found"
    exit 1
  }

  echo -e "${GREEN}[+] Reading pcap file: $TARGET${RESET}"
  echo

  tcpdump -r "$TARGET" -nn -vv $TCPDUMP_FILTER | pretty_print
fi
