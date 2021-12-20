import json
import socket
import requests
from graph_crdt.config import Config
from graph_crdt.utils import get_logger
from graph_crdt.graph import database_instance

logger = get_logger("Worker")


class DatabaseWorker:
    def __init__(self, socket_internal):
        self.socket_internal = socket_internal
        self.bufferSize = Config.BUFFER_SIZE
        self.UDPServerSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)

    def response(self, res, address):
        msg = json.dumps(res)
        msg = str.encode(msg)
        self.UDPServerSocket.sendto(msg, address)

    def execute(self):
        self.UDPServerSocket.bind(self.socket_internal)

        logger.info(f"Broadcaster listening at {self.socket_internal}")
        msg = "Copy! I am on the way"
        while True:
            bytes_address_pair = self.UDPServerSocket.recvfrom(self.bufferSize)
            message, address = bytes_address_pair

            message = message.decode("utf-8")
            message = json.loads(message)

            if message["query"] == "merge":
                database_instance.merge(message["vertices_added"], message["vertices_removed"], message["edges_added"],
                                        message["edges_removed"])
                self.response({"data": f"Successfully merged!"}, address)

                friends = message["friend_list"]
                logger.info(friends)
                for friend in friends:
                    if friend == message["your_address"] or friend == message["from_addr"]:
                        continue

                    data = {
                        "uuid": message["uuid"],
                        "from_addr": message["your_address"],
                        "vertices_added": message["vertices_added"],
                        "vertices_removed": message["vertices_removed"],
                        "edges_added": message["edges_added"],
                        "edges_removed": message["edges_removed"]
                    }

                    logger.debug(f"Broadcasting merge request to {friend}")
                    response = requests.post(f"{friend}/merge", data=data, timeout=Config.REQUEST_TIMEOUT)
                    logger.info(f"Broadcasted merge request to {friend}: {response.json()}")

                logger.info("Successfully merged!")
            elif message["query"] == "set_dir":
                database_instance.set_dir(bool(message["dir"]))
                res = {
                    "data": "Success"
                }
                self.response(res, address)
                logger.info("Successfully set direction")
            elif message["query"] == "broadcast":
                data = database_instance.broadcast()
                data["uuid"] = message["uuid"]
                data["from_addr"] = message["from_addr"]

                friend = message["to"]
                response = requests.post(f"{friend}/merge", data=data, timeout=Config.REQUEST_TIMEOUT)

                res = {
                    "status": response.json()["status"]
                }
                self.response(res, address)
                logger.info("Broadcasted")
            elif message["query"] == "add_vertex":
                u = int(message["u"])
                status, _ = database_instance.add_vertex(u)
                res = {
                    "status": status,
                    "_": _
                }

                self.response(res, address)
                logger.info(f"Successfully added vertex {u}")
            elif message["query"] == "add_edge":
                u = int(message["u"])
                v = int(message["v"])

                status, _ = database_instance.add_edge(u, v)
                res = {
                    "status": status,
                    "_": _
                }

                self.response(res, address)
                logger.info(f"Successfully added edge {u} - {v}")
            elif message["query"] == "remove_vertex":
                u = int(message["u"])
                status = database_instance.remove_vertex(u)

                res = {
                    "status": status
                }

                self.response(res, address)
                logger.info(f"Successfully removed vertex {u}")
            elif message["query"] == "remove_edge":
                u = int(message["u"])
                v = int(message["v"])

                status = database_instance.remove_edge(u, v)
                res = {
                    "status": status
                }

                self.response(res, address)
                logger.info(f"Successfully removed edge {u} - {v}")
            elif message["query"] == "exists_vertex":
                u = int(message["u"])
                _, status = database_instance.contains_vertex(u)

                res = {
                    "_": _,
                    "status": status
                }

                self.response(res, address)
                logger.info(f"Successfully check exists {u}")
            elif message["query"] == "exists_edge":
                u = int(message["u"])
                v = int(message["v"])

                _, status = database_instance.contains_edge(u, v)
                res = {
                    "_": _,
                    "status": status
                }

                self.response(res, address)
                logger.info(f"Successfully check exists {u} - {v}")
            elif message["query"] == "get_neighbors":
                u = int(message["u"])

                _, status = database_instance.get_neighbors(u)
                res = {
                    "_": _,
                    "status": status
                }

                self.response(res, address)
                logger.info(f"Successfully get neighbors {u}")
            elif message["query"] == "find_path":
                u = int(message["u"])
                v = int(message["v"])

                status, path = database_instance.find_path(u, v)
                res = {
                    "status": status,
                    "path": path
                }

                self.response(res, address)
                logger.info(f"Successfully find path from {u} to {v}")
            elif message["query"] == "get_friend":
                data = database_instance.get_cluster_table()

                res = {
                    "data": data
                }

                self.response(res, address)
                logger.info(f"Successfully get friend")
            elif message["query"] == "clear":
                data = database_instance.clear()

                res = {
                    "data": data
                }
                self.response(res, address)
                logger.info(f"Successfully clear database")
            elif message["query"] == "register":
                addr = message["to"]
                self.response({"data": "Success"}, address)
                response = requests.post(f"{addr}/register",
                                         data={"their_address": message["data"],
                                               "my_address": message["from"]},
                                         timeout=Config.REQUEST_TIMEOUT)
                response = response.json()["status"]

                f, t, d = message["from"], message["to"], message["data"]
                logger.info(f"Broadcasted from {f} to {t} with {d}: {response}")
            else:
                continue
