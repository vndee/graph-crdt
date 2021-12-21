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

![](https://i.imgur.com/F0FxMu8.png)

![](https://i.imgur.com/brmnztR.png)

```bash
docker build -t gcrdt .
```

```bash 
./run.sh
```
