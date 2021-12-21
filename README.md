## graph-crdt
A portable on-memory conflict-free replicated graph database

This project is a simple implementation of a conflict-free replicated graph database. The graph opeerations has been developed based on Last-Writer-Wins element set, which contains serveral basic operation as follow:

- add a vertex/edge
- remove a vertex/edge
- check if a vertex/edge is in the graph
- query for all vertices connected to a vertex
- find any path between two vertices
- merge with concurrent changes from other graph/replica.

This project come with a fully decentralization fashion which can merging data without any cordination between replicas. The core idea of this project is that each replica can work independently and when the replica connect to the database network, they can merge or receive updates from other replicas via the connection in the network. When a replica start, it should be assigned by an address and know exactly one friend (replica) who has already connected to the network. When a replica in the network receive a message that its friend has just registered to the network, it will broadcast information of this newcomer to the network and this message is sent to all network via connection between replica. This process keep the network always connected. When a replica send a merge request to the network, this message is also sent to all replicas since the network is always connected.

### Installation

Build docker image for the database instance:

```bash
docker build -t gcrdt .
```

Run the first database instance, it should be noted that the first instance of the network has no friend here, so we set `FRIEND_ADDRESS=-1`:
```bash
docker run -d --name cluster_1 -p 8081:8000 -e ADDRESS=http://host.docker.internal:8081 -e FRIEND_ADDRESS=-1 gcrdt
```
Due to the limitations of Docker for MacOS (https://docs.docker.com/desktop/mac/networking/), we should use `http://host.docker.internal` as the host name, in the other platform like linux we can use `http://127.0.0.1` of `http://localhost` instead.
 
From the second instance (replica), if we want it connected to the network of the first instance, we must set `FRIEND_ADDRESS` variable as the address of the instance which is already in the network. For example:

```bash
docker run -d --name cluster_2 -p 8082:8000 -e ADDRESS=http://host.docker.internal:8082 -e FRIEND_ADDRESS=http://host.docker.internal:8081 gcrdt

docker run -d --name cluster_3 -p 8083:8000 -e ADDRESS=http://host.docker.internal:8083 -e FRIEND_ADDRESS=http://host.docker.internal:8082 gcrdt
```

After these commaned are executed, cluster_1, cluster_3, cluster_3 is conntected together. We can also run the sample script to have a network with 5 replicas (instance):
```bash
chmod +x run.sh
./run.sh
```

![](https://i.imgur.com/brmnztR.png)

![](https://i.imgur.com/F0FxMu8.png)

Client:
```bash
python setup.py install
```


```bash 
./run.sh
```
