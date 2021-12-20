from graph_crdt import DatabaseGateway

if __name__ == "__main__":
    database = DatabaseGateway()
    # database.execute(host="0.0.0.0", port=8000, your_address="http://127.0.0.1:8000")
    # database.execute(host="0.0.0.0", port=8001, your_address="http://127.0.0.1:8001",
    #                  friend_address="http://127.0.0.1:8000")
    # database.execute(host="0.0.0.0", port=8002, your_address="http://127.0.0.1:8002",
    #                  friend_address="http://127.0.0.1:8000")
    database.execute(host="0.0.0.0", port=8003, your_address="http://127.0.0.1:8003",
                     friend_address="http://127.0.0.1:8002", socket_internal=("127.0.0.1", 20003))
