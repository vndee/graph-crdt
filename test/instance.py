from graph_crdt import DatabaseCluster

if __name__ == "__main__":
    database = DatabaseCluster()
    # database.execute(host="0.0.0.0", port=8000, your_address="http://127.0.0.1:8000")
    # database.execute(host="0.0.0.0", port=8001, your_address="http://127.0.0.1:8001",
    #                  friend_address="http://127.0.0.1:8000")
    database.execute(host="0.0.0.0", port=8002, your_address="http://127.0.0.1:8002",
                     friend_address="http://127.0.0.1:8000")
