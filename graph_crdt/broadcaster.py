import json
import socket
import requests
from graph_crdt.config import Config
from graph_crdt.utils import get_logger
from graph_crdt.graph import database_instance

logger = get_logger("Broadcaster")


class DatabaseBroadcaster:
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
            # bytes_to_send = str.encode(f"{msg} {address}")
            # self.UDPServerSocket.sendto(bytes_to_send, address)

            message = message.decode("utf-8")
            message = json.loads(message)

            if message["query"] == "merge":
                database_instance.merge(message["vertices_added"], message["vertices_removed"], message["edges_added"],
                                        message["edges_removed"])
                logger.info(database_instance.get_cluster_table())
                # for friend in database_instance.get_cluster_table():
                #     if friend == DatabaseGateway.your_address or friend == from_addr:
                #         continue
                #
                #     data["from_addr"] = DatabaseGateway.your_address
                #     logger.debug(f"Broadcasting to {friend}")
                #     response = requests.post(f"{friend}/merge", data=data)
                #     logger.info(f"Broadcasted merge request to {friend}: {response.json()}")

                logger.info("Successfully merged!")
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
                pass
            elif message["query"] == "remove_vertex":
                # TODO
                pass
            elif message["query"] == "remove_edge":
                # TODO
                pass
            elif message["query"] == "exists_vertex":
                # TODO
                pass
            elif message["query"] == "exists_edge":
                # TODO
                pass
            elif message["query"] == "get_neighbors":
                # TODO
                pass
            elif message["query"] == "find_path":
                # TODO
                pass
            elif message["query"] == "get_friend":
                # TODO
                pass
            elif message["query"] == "clear":
                # TODO
                pass
            elif message["query"] == "register":
                addr = message["to"]
                response = requests.post(f"{addr}/register",
                                         data={"their_address": message["data"],
                                               "my_address": message["from"]},
                                         timeout=3)
                response = response.json()["status"]

                f, t, d = message["from"], message["to"], message["data"]
                logger.info(f"Broadcasted from {f} to {t} with {d}: {response}")
            else:
                continue

        # TODO: add timeout to ignore death cluster
        # send request broadcast to friends
