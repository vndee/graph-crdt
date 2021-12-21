import json
import uuid
import socket
import uvicorn
import requests
from graph_crdt.config import Config
from fastapi import FastAPI, Form
from fastapi.middleware.cors import CORSMiddleware
from graph_crdt.utils import get_logger


logger = get_logger("Database Instance")


class ResponseStatus:
    success = "Success"
    error = "Error"
    error_default_msg = "An error occurred"


class DatabaseGateway:
    communication_server: FastAPI = FastAPI(title="Portable on-memory conflict-free replicated graph database",
                                            contact={
                                                "name": "Duy Huynh",
                                                "email": "vndee.huynh@gmail.com",
                                            })

    communication_server.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    your_address = None
    friend_address = None
    bidirection = True
    UDPClientSocket = None
    socket_internal = None
    merged_uuid = set()
    cluster_table = []
    address_set = set()

    @staticmethod
    def send_socket(data):
        """
        Send message from REST gateway to UDP socket worker
        :param data: message content as dictionary
        :return: received message from UDP socket worker
        """
        msg = json.dumps(data)
        msg = str.encode(msg)
        DatabaseGateway.UDPClientSocket.sendto(msg, DatabaseGateway.socket_internal)
        rcv_msg = DatabaseGateway.UDPClientSocket.recvfrom(Config.BUFFER_SIZE)
        return rcv_msg

    @staticmethod
    def register_cluster_table(address):
        """
        Add newcomer address to friend list
        :param address:
        :return:
        """
        if address not in DatabaseGateway.address_set:
            DatabaseGateway.cluster_table.append(address)
            DatabaseGateway.address_set.add(address)
            return True

        return False

    @staticmethod
    @communication_server.on_event("startup")
    async def startup_event():
        """
        REST gateway startup event
        :return:
        """
        data = {
            "query": "set_dir",
            "dir": DatabaseGateway.bidirection
        }
        _ = DatabaseGateway.send_socket(data)

        logger.info("Initialized CRDTGraph database instance!")
        logger.info(f"Communication server listening at {DatabaseGateway.your_address}")
        logger.info(f"Socket tunnel listening at {DatabaseGateway.socket_internal}")

        if DatabaseGateway.friend_address is not None:
            # let friend know we are connected to the network
            _ = DatabaseGateway.register_cluster_table(DatabaseGateway.friend_address)
            response = requests.post(f"{DatabaseGateway.friend_address}/register",
                                     data={"their_address": DatabaseGateway.your_address,
                                           "my_address": DatabaseGateway.your_address})
            response = response.json()["status"]

            logger.info(f"Register to {DatabaseGateway.friend_address}: {response}")

    @staticmethod
    def execute(host: str = "0.0.0.0", port: int = 8000, your_address=None, friend_address=None, bidirection=True,
                socket_internal=None):
        """
        Execute REST gateway
        :param host:
        :param port:
        :param your_address:
        :param friend_address:
        :param bidirection:
        :param socket_internal:
        :return:
        """
        DatabaseGateway.bidirection = bidirection
        DatabaseGateway.your_address = your_address
        DatabaseGateway.friend_address = friend_address
        DatabaseGateway.UDPClientSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        DatabaseGateway.socket_internal = socket_internal

        while host[-1] == "/":
            host = host[: -1]

        uvicorn.run(app=DatabaseGateway.communication_server, port=port, host=host)

    @staticmethod
    def response(status, success_msg, data="", error_msg=ResponseStatus.error_default_msg):
        if status:
            logger.info(success_msg)
            return {
                "status": ResponseStatus.success,
                "data": data,
                "message": success_msg
            }
        else:
            logger.info(error_msg)
            return {
                "status": ResponseStatus.error,
                "data": data,
                "message": error_msg
            }

    @staticmethod
    @communication_server.get("/")
    async def status():
        return {
            "message": "OK!"
        }

    @staticmethod
    @communication_server.post("/register/")
    async def register(their_address: str = Form(...),
                       my_address: str = Form(...)):
        """
        Listening for a friend who are new in the network to help them connect to the network
        :param their_address:
        :param my_address:
        :return:
        """
        f = DatabaseGateway.register_cluster_table(their_address)
        if f is False:
            return DatabaseGateway.response("Success", "Cluster address has already been registered!")

        for addr in DatabaseGateway.cluster_table:
            # let other friends knows our new friend has just connected
            if addr != their_address and addr != my_address:
                logger.info(f"Broadcasting newcomer {their_address} to {addr}")

                data = {
                    "query": "register",
                    "from": DatabaseGateway.your_address,
                    "to": addr,
                    "data": their_address
                }

                rcv_msg = DatabaseGateway.send_socket(data)
                logger.info(f"Received message: {rcv_msg}")

        logger.info(f"Successfully registered and broadcasted: {their_address}")
        return DatabaseGateway.response("Success", "Successfully register cluster address")

    @staticmethod
    def decode(msg):
        msg = msg.decode("utf-8")
        return json.loads(msg)

    @staticmethod
    @communication_server.get("/add_vertex/{u}")
    async def add_vertex(u: int):
        data = {
            "query": "add_vertex",
            "u": u
        }

        rcv_msg = DatabaseGateway.send_socket(data)
        rcv_msg = DatabaseGateway.decode(rcv_msg[0])
        status, _ = rcv_msg["status"], rcv_msg["_"]

        return DatabaseGateway.response(status, f"Successfully added vertex {u}", error_msg=_)

    @staticmethod
    @communication_server.get("/add_edge/{u}/{v}")
    async def add_edge(u: int, v: int):
        data = {
            "query": "add_edge",
            "u": u,
            "v": v
        }

        rcv_msg = DatabaseGateway.send_socket(data)
        rcv_msg = DatabaseGateway.decode(rcv_msg[0])
        status, _ = rcv_msg["status"], rcv_msg["_"]

        return DatabaseGateway.response(status, f"Successfully added edge {u}-{v}", error_msg=_)

    @staticmethod
    @communication_server.get("/remove_vertex/{u}")
    async def remove_vertex(u: int):
        data = {
            "query": "remove_vertex",
            "u": u
        }

        rcv_msg = DatabaseGateway.send_socket(data)
        rcv_msg = DatabaseGateway.decode(rcv_msg[0])
        status = rcv_msg["status"]

        return DatabaseGateway.response(status, f"Successfully removed vertex {u}")

    @staticmethod
    @communication_server.get("/remove_edge/{u}/{v}")
    async def remove_edge(u: int, v: int):
        data = {
            "query": "remove_edge",
            "u": u,
            "v": v
        }

        rcv_msg = DatabaseGateway.send_socket(data)
        rcv_msg = DatabaseGateway.decode(rcv_msg[0])
        status = rcv_msg["status"]

        return DatabaseGateway.response(status, f"Successfully removed edge {u}-{v}")

    @staticmethod
    @communication_server.get("/check_exists/{u}")
    async def exists_vertex(u: int):
        data = {
            "query": "exists_vertex",
            "u": u
        }

        rcv_msg = DatabaseGateway.send_socket(data)
        rcv_msg = DatabaseGateway.decode(rcv_msg[0])
        status, _ = rcv_msg["status"], rcv_msg["_"]

        return DatabaseGateway.response(_, data=status, success_msg=f"check_exists {u}: {status}")

    @staticmethod
    @communication_server.get("/check_exists/{u}/{v}")
    async def exists_edge(u: int, v: int):
        data = {
            "query": "exists_edge",
            "u": u,
            "v": v
        }

        rcv_msg = DatabaseGateway.send_socket(data)
        rcv_msg = DatabaseGateway.decode(rcv_msg[0])
        status, _ = rcv_msg["status"], rcv_msg["_"]

        return DatabaseGateway.response(_, data=status, success_msg=f"check_exists {u}-{v}: {status}")

    @staticmethod
    @communication_server.get("/get_neighbors/{u}")
    async def get_neighbors(u: int):
        data = {
            "query": "get_neighbors",
            "u": u
        }

        rcv_msg = DatabaseGateway.send_socket(data)
        rcv_msg = DatabaseGateway.decode(rcv_msg[0])
        status, _ = rcv_msg["status"], rcv_msg["_"]

        return DatabaseGateway.response(_, data=status, success_msg=f"Successfully get neighbors of {status}")

    @staticmethod
    @communication_server.get("/find_path/{u}/{v}")
    async def find_path(u: int, v: int):
        data = {
            "query": "find_path",
            "u": u,
            "v": v
        }

        rcv_msg = DatabaseGateway.send_socket(data)
        rcv_msg = DatabaseGateway.decode(rcv_msg[0])
        status, path = rcv_msg["status"], rcv_msg["path"]

        return DatabaseGateway.response(status, data=path,
                                        success_msg=f"Successfully finding path from {u} to {v}: {path}",
                                        error_msg=f"Could not found path from {u} to {v}")

    @staticmethod
    @communication_server.get("/broadcast")
    async def broadcast():
        uid = str(uuid.uuid4())
        data = {
            "query": "broadcast",
            "uuid": uid,
            "from_addr": DatabaseGateway.your_address
        }
        DatabaseGateway.merged_uuid.add(data["uuid"])

        for friend in DatabaseGateway.cluster_table:
            # send to other friend new updates
            data["to"] = friend
            rcv_msg = DatabaseGateway.send_socket(data)
            rcv_msg = DatabaseGateway.decode(rcv_msg[0])["status"]

            logger.info(f"Broadcasted merge request to {friend}: {rcv_msg}")

        return DatabaseGateway.response("Success", data=data,
                                        success_msg=f"Successfully broadcast with uuid: {uid}")

    @staticmethod
    @communication_server.get("/get_friend")
    async def get_friend():
        return DatabaseGateway.response("Success", data=DatabaseGateway.cluster_table,
                                        success_msg="Successfully returned friend list")

    @staticmethod
    @communication_server.get("/clear")
    async def clear():
        data = {
            "query": "clear"
        }

        rcv_msg = DatabaseGateway.send_socket(data)
        rcv_msg = DatabaseGateway.decode(rcv_msg[0])
        status = rcv_msg["data"]

        return DatabaseGateway.response(status, data=status, success_msg="Successfully clear database")

    @staticmethod
    @communication_server.post("/merge")
    async def merge(uuid=Form(...),
                    from_addr=Form(...),
                    vertices_added=Form(...),
                    vertices_removed=Form(...),
                    edges_added=Form(...),
                    edges_removed=Form(...)):
        if uuid in DatabaseGateway.merged_uuid:
            return DatabaseGateway.response("Success", data="[]",
                                            success_msg=f"This uuid {uuid} has already been merged")

        DatabaseGateway.merged_uuid.add(uuid)
        data = {
            "your_address": DatabaseGateway.your_address,
            "from_addr": from_addr,
            "query": "merge",
            "uuid": uuid,
            "vertices_added": vertices_added,
            "vertices_removed": vertices_removed,
            "edges_added": edges_added,
            "edges_removed": edges_removed,
            "friend_list": DatabaseGateway.cluster_table
        }

        rcv_msg = DatabaseGateway.send_socket(data)
        rcv_msg = DatabaseGateway.decode(rcv_msg[0])["data"]
        logger.info(f"Received message: {rcv_msg}")

        return DatabaseGateway.response("Success", data="True", success_msg="Successfully merged!")
