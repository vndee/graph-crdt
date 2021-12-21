import argparse
from graph_crdt import DatabaseGateway
from graph_crdt import DatabaseWorker

if __name__ == "__main__":
    args = argparse.ArgumentParser(description="Graph CRDT Executor")
    args.add_argument("-e", "--executor", type=str, default="gateway", help="Executor type")
    args.add_argument("-a", "--address", type=str, default="http://127.0.0.1:8000", help="Cluster address")
    args.add_argument("-f", "--friend_address", type=str, default=None, help="Friend address")
    args = args.parse_args()
    print(args)

    if args.executor == "gateway":
        instance = DatabaseGateway()
        if args.friend_address == "-1":
            args.friend_address = None
        instance.execute(host="0.0.0.0", port=8000, your_address=args.address, friend_address=args.friend_address,
                         socket_internal=("127.0.0.1", 20000))
    else:
        instance = DatabaseWorker(socket_internal=("127.0.0.1", 20000))
        instance.execute()
