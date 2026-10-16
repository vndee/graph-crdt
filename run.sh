#!/bin/bash
set -euo pipefail

# Peers use container DNS on Linux and Docker Desktop; clients use loopback ports.
network=gcrdt-demo
image=${GRAPH_CRDT_IMAGE:-gcrdt}
for node in 1 2 3 4 5; do
    if docker container inspect "cluster_$node" >/dev/null 2>&1; then
        echo "cluster_$node already exists; stop/remove the previous demo first." >&2
        exit 1
    fi
done
if ! docker network inspect "$network" >/dev/null 2>&1; then
    docker network create "$network" >/dev/null
fi

friends=(-1 http://cluster_1:8000 http://cluster_2:8000 http://cluster_1:8000 http://cluster_4:8000)
for node in 1 2 3 4 5; do
    port=$((8080 + node))
    docker run -d --name "cluster_$node" --network "$network" \
        -p "127.0.0.1:$port:8000" \
        -e ADDRESS="http://cluster_$node:8000" -e FRIEND_ADDRESS="${friends[$((node - 1))]}" \
        -e NO_PROXY=localhost,127.0.0.1,cluster_1,cluster_2,cluster_3,cluster_4,cluster_5 \
        -e no_proxy=localhost,127.0.0.1,cluster_1,cluster_2,cluster_3,cluster_4,cluster_5 \
        "$image" >/dev/null
    ready=false
    for attempt in {1..60}; do
        if curl --noproxy '*' --fail --silent --connect-timeout 1 --max-time 1 \
                "http://127.0.0.1:$port/" >/dev/null; then
            ready=true
            break
        fi
        if [ "$(docker inspect --format '{{.State.Running}}' "cluster_$node")" != true ]; then
            break
        fi
        sleep 0.25
    done
    if [ "$ready" != true ]; then
        docker logs "cluster_$node" >&2
        echo "cluster_$node did not become ready" >&2
        exit 1
    fi
    echo "cluster_$node ready on http://127.0.0.1:$port"
done
