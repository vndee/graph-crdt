#!/bin/bash
set -euo pipefail
worker_pid=
gateway_pid=
cleanup() {
    for process in "$gateway_pid" "$worker_pid"; do
        if [ -n "$process" ]; then kill "$process" 2>/dev/null || true; fi
    done
    wait 2>/dev/null || true
}
trap cleanup EXIT
trap 'exit 143' TERM
trap 'exit 130' INT

python3 graph_crdt/executor.py -e worker &
worker_pid=$!
# UDP has no connection handshake. Retry a read-only request before the gateway
# sends its one-shot set_dir command, otherwise an early packet can be lost.
python3 - <<'PY'
import json
import socket
import time

deadline = time.monotonic() + 15
with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as probe:
    probe.settimeout(0.25)
    while time.monotonic() < deadline:
        probe.sendto(b'{"query":"get_friend"}', ("127.0.0.1", 20000))
        try:
            response, _ = probe.recvfrom(2048)
            if "data" in json.loads(response):
                break
        except socket.timeout:
            continue
    else:
        raise SystemExit("UDP worker did not become ready")
PY
python3 graph_crdt/executor.py -e gateway -a "$1" -f "$2" &
gateway_pid=$!
wait -n "$worker_pid" "$gateway_pid"
