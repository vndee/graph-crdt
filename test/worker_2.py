from graph_crdt.worker import DatabaseWorker


if __name__ == "__main__":
    broadcaster = DatabaseWorker(socket_internal=("127.0.0.1", 20001))
    broadcaster.execute()
