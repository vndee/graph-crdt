#!/bin/bash

docker run -d --name cluster_1 -p 8081:8000 -e ADDRESS=http://host.docker.internal:8081 -e FRIEND_ADDRESS=-1 gcrdt

docker run -d --name cluster_2 -p 8082:8000 -e ADDRESS=http://host.docker.internal:8082 -e FRIEND_ADDRESS=http://host.docker.internal:8081 gcrdt

docker run -d --name cluster_3 -p 8083:8000 -e ADDRESS=http://host.docker.internal:8083 -e FRIEND_ADDRESS=http://host.docker.internal:8082 gcrdt

docker run -d --name cluster_4 -p 8084:8000 -e ADDRESS=http://host.docker.internal:8084 -e FRIEND_ADDRESS=http://host.docker.internal:8081 gcrdt

docker run -d --name cluster_5 -p 8085:8000 -e ADDRESS=http://host.docker.internal:8085 -e FRIEND_ADDRESS=http://host.docker.internal:8084 gcrdt
