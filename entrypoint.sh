#!/bin/bash

python3 graph_crdt/executor.py -e worker &
python3 graph_crdt/executor.py -e gateway -a $1 -f $2 &

wait -n

exit $?
# docker run -p 8082:8000 -e ADDRESS=http://host.docker.internal:8082 -e FRIEND_ADDRESS=http://host.docker.internal:8081 gcrdt
