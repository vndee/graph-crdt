import json
import uuid
import socket
import uvicorn
import requests
from graph_crdt.config import Config
from fastapi import FastAPI, Form
from graph_crdt import CRDTGraph
from fastapi.middleware.cors import CORSMiddleware
from graph_crdt.utils import get_logger
from graph_crdt.graph import database_instance

# from test.udp_client import UDPClientSocket

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

    @staticmethod
    def send_socket(data):
        msg = json.dumps(data)
        msg = str.encode(msg)
        DatabaseGateway.UDPClientSocket.sendto(msg, DatabaseGateway.socket_internal)
        rcv_msg = DatabaseGateway.UDPClientSocket.recvfrom(Config.BUFFER_SIZE)
        return rcv_msg

    @staticmethod
    @communication_server.on_event("startup")
    async def startup_event():
        database_instance.set_dir(DatabaseGateway.bidirection)

        logger.info("Initialized CRDTGraph database instance!")
        logger.info(f"Communication server listening at {DatabaseGateway.your_address}")
        logger.info(f"Socket tunnel listening at {DatabaseGateway.socket_internal}")

        if DatabaseGateway.friend_address is not None:
            # let friend know you are connected to the network
            database_instance.register_cluster_table(address=DatabaseGateway.friend_address)

            response = requests.post(f"{DatabaseGateway.friend_address}/register",
                                     data={"their_address": DatabaseGateway.your_address,
                                           "my_address": DatabaseGateway.your_address})
            response = response.json()["status"]

            logger.info(f"Register to {DatabaseGateway.friend_address}: {response}")

    @staticmethod
    def execute(host: str = "0.0.0.0", port: int = 8000, your_address=None, friend_address=None, bidirection=True,
                socket_internal=None):
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
        # TODO: send to broadcaster and immediately response
        f = database_instance.register_cluster_table(their_address)
        if f is False:
            return DatabaseGateway.response("Success", "Cluster address has already been registered!")

        # print(f"their_addr: {their_address}")
        # print(f"my_addr: {DatabaseGateway.your_address}")
        # print(f"cls_table: {DatabaseGateway.database_instance.get_cluster_table()}")
        # print(DatabaseGateway.UDPClientSocket)
        for addr in database_instance.get_cluster_table():
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

                # response = requests.post(f"{addr}/register",
                #                          data={"their_address": their_address,
                #                                "my_address": DatabaseGateway.your_address},
                #                          timeout=0.0000000001)
                # response = response.json()["status"]

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
        status = database_instance.remove_vertex(u)
        return DatabaseGateway.response(status, f"Successfully removed vertex {u}")

    @staticmethod
    @communication_server.get("/remove_edge/{u}/{v}")
    async def remove_edge(u: int, v: int):
        status = database_instance.remove_edge(u, v)
        return DatabaseGateway.response(status, f"Successfully removed edge {u}-{v}")

    @staticmethod
    @communication_server.get("/check_exists/{u}")
    async def exists_vertex(u: int):
        _, status = database_instance.contains_vertex(u)
        return DatabaseGateway.response(_, data=status, success_msg=f"check_exists {u}: {status}")

    @staticmethod
    @communication_server.get("/check_exists/{u}/{v}")
    async def exists_edge(u: int, v: int):
        _, status = database_instance.contains_edge(u, v)
        return DatabaseGateway.response(_, data=status, success_msg=f"check_exists {u}-{v}: {status}")

    @staticmethod
    @communication_server.get("/get_neighbors/{u}")
    async def get_neighbors(u: int):
        _, status = database_instance.get_neighbors(u)
        return DatabaseGateway.response(_, data=status, success_msg=f"Successfully get neighbors of {status}")

    @staticmethod
    @communication_server.get("/find_path/{u}/{v}")
    async def find_path(u: int, v: int):
        status, path = database_instance.find_path(u, v)
        return DatabaseGateway.response(status, data=path,
                                        success_msg=f"Successfully finding path from {u} to {v}: {path}",
                                        error_msg=f"Could not found path from {u} to {v}")

    @staticmethod
    @communication_server.get("/broadcast")
    async def broadcast():
        data = database_instance.broadcast()
        data["uuid"] = str(uuid.uuid4())
        data["from_addr"] = DatabaseGateway.your_address

        for friend in database_instance.get_cluster_table():
            response = requests.post(f"{friend}/merge", data=data)
            logger.info(f"{response.json()}")

        return DatabaseGateway.response("Success", data=data,
                                        success_msg="Successfully broadcast")

    @staticmethod
    @communication_server.get("/get_friend")
    async def get_friend():
        data = database_instance.get_cluster_table()
        return DatabaseGateway.response("Success", data=data, success_msg="Successfully returned friend list")

    @staticmethod
    @communication_server.get("/clear")
    async def clear():
        status = database_instance.clear()
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
        print(DatabaseGateway.merged_uuid)
        print(uuid)
        print(from_addr)
        print(vertices_added)
        print(vertices_removed)
        print(edges_added)
        print(edges_removed)
        data = {
            "query": "merge",
            "uuid": uuid,
            "vertices_added": vertices_added,
            "vertices_removed": vertices_removed,
            "edges_added": edges_added,
            "edges_removed": edges_removed
        }

        rcv_msg = DatabaseGateway.send_socket(data)
        logger.info(f"Received message: {rcv_msg}")

        data["friend_list"] = database_instance.get_cluster_table()

        return DatabaseGateway.response("Success", data="True", success_msg="Successfully merged!")
