#!/usr/bin/env bash
# =====================================================================
# nmap_ultimate.sh — Full Nmap Power Wrapper
# Author: ChatGPT & Mr. Samsoft
# Purpose: Authorized, professional network assessment & research
# =====================================================================

set -euo pipefail

# -------------------------
# Defaults
# -------------------------
TARGET=""
OUTDIR="nmap_results"
PROFILE="custom"
SCRIPTS=""
PORTS=""
TIMING="-T4"
IPV6=false
UDP=false
OS=false
VERSION=false
ALL_PORTS=false
PING_SCAN=false
NO_PING=false
AGGRESSIVE=false
DECOYS=""
SPOOF_IP=""
FRAG=false
MTU=""
SOURCE_PORT=""
EXTRA=""
DATE="$(date +%Y%m%d_%H%M%S)"

# -------------------------
# Usage
# -------------------------
usage() {
cat <<'EOF'
Usage:
  ./nmap_ultimate.sh -t <target> [options]

Targets:
  IP, CIDR, hostname, or file

Core Options:
  -t <target>        Target (required)
  -p <ports>         Port list or range (e.g. 22,80,443 or 1-65535)
  --all-ports        Scan all TCP ports
  --udp              Enable UDP scan
  --ipv6             Enable IPv6
  --ping             Host discovery only
  --no-ping          Skip host discovery
  -A                 Aggressive scan (OS, version, scripts, traceroute)

Detection:
  --os               OS detection
  --version          Service/version detection

Scripts:
  --scripts <set>    NSE scripts (safe, vuln, auth, brute, discovery, all)

Timing:
  -T0..-T5           Timing template (default T4)

Evasion (authorized use only):
  --decoy <list>     Decoy IPs (e.g. RND:5 or 1.1.1.1,2.2.2.2)
  --spoof <ip>       Spoof source IP
  --frag             Packet fragmentation
  --mtu <size>       Custom MTU
  --source-port <p>  Spoof source port

Output:
  -o <dir>           Output directory (default: nmap_results)

Advanced:
  -x "<args>"        Raw Nmap arguments passthrough

Examples:
  ./nmap_ultimate.sh -t 192.168.1.0/24 --ping
  ./nmap_ultimate.sh -t target.com -A
  ./nmap_ultimate.sh -t targets.txt --all-ports --scripts vuln
  ./nmap_ultimate.sh -t host --udp -p 53,123

NOTE:
  Use ONLY on networks you own or have written authorization for.
EOF
exit 1
}

# -------------------------
# Parse arguments
# -------------------------
while [[ $# -gt 0 ]]; do
  case "$1" in
    -t) TARGET="$2"; shift 2 ;;
    -p) PORTS="$2"; shift 2 ;;
    --all-ports) ALL_PORTS=true; shift ;;
    --udp) UDP=true; shift ;;
    --ipv6) IPV6=true; shift ;;
    --ping) PING_SCAN=true; shift ;;
    --no-ping) NO_PING=true; shift ;;
    -A) AGGRESSIVE=true; shift ;;
    --os) OS=true; shift ;;
    --version) VERSION=true; shift ;;
    --scripts) SCRIPTS="$2"; shift 2 ;;
    -T*) TIMING="$1"; shift ;;
    --decoy) DECOYS="$2"; shift 2 ;;
    --spoof) SPOOF_IP="$2"; shift 2 ;;
    --frag) FRAG=true; shift ;;
    --mtu) MTU="$2"; shift 2 ;;
    --source-port) SOURCE_PORT="$2"; shift 2 ;;
    -o) OUTDIR="$2"; shift 2 ;;
    -x) EXTRA="$2"; shift 2 ;;
    -h|--help) usage ;;
    *) echo "[!] Unknown option: $1"; usage ;;
  esac
done

[[ -z "$TARGET" ]] && usage
mkdir -p "$OUTDIR"
OUT="$OUTDIR/nmap_${DATE}"

# -------------------------
# Build command
# -------------------------
CMD="nmap $TIMING"

[[ "$IPV6" == true ]] && CMD+=" -6"
[[ "$PING_SCAN" == true ]] && CMD+=" -sn"
[[ "$NO_PING" == true ]] && CMD+=" -Pn"
[[ "$UDP" == true ]] && CMD+=" -sU"
[[ "$OS" == true ]] && CMD+=" -O"
[[ "$VERSION" == true ]] && CMD+=" -sV"
[[ "$AGGRESSIVE" == true ]] && CMD+=" -A"

[[ "$ALL_PORTS" == true ]] && CMD+=" -p-"
[[ -n "$PORTS" ]] && CMD+=" -p $PORTS"

[[ -n "$SCRIPTS" ]] && CMD+=" --script=$SCRIPTS"
[[ -n "$DECOYS" ]] && CMD+=" -D $DECOYS"
[[ -n "$SPOOF_IP" ]] && CMD+=" -S $SPOOF_IP"
[[ "$FRAG" == true ]] && CMD+=" -f"
[[ -n "$MTU" ]] && CMD+=" --mtu $MTU"
[[ -n "$SOURCE_PORT" ]] && CMD+=" --source-port $SOURCE_PORT"

CMD+=" $EXTRA"

# Target handling
[[ -f "$TARGET" ]] && CMD+=" -iL $TARGET" || CMD+=" $TARGET"

# Output
CMD+=" -oA $OUT"

# -------------------------
# Execute
# -------------------------
echo "================================================="
echo " Nmap Ultimate Wrapper"
echo " Author : ChatGPT & Mr. Samsoft"
echo " Target : $TARGET"
echo " Output : $OUT"
echo "================================================="
echo
echo "[*] Command:"
echo "$CMD"
echo
eval "$CMD"

echo
echo "[✓] Scan complete"
echo "[✓] Files generated:"
echo "    $OUT.nmap"
echo "    $OUT.gnmap"
echo "    $OUT.xml"
