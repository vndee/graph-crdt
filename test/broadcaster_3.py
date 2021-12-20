from graph_crdt.broadcaster import DatabaseBroadcaster


if __name__ == "__main__":
    broadcaster = DatabaseBroadcaster(socket_internal=("127.0.0.1", 20002))
    broadcaster.execute()
