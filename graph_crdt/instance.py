import uvicorn
import requests
from fastapi import FastAPI, Form
from graph_crdt import CRDTGraph
from fastapi.middleware.cors import CORSMiddleware
from graph_crdt.utils import get_logger

logger = get_logger("Database Instance")


class ResponseStatus:
    success = "Success"
    error = "Error"
    error_default_msg = "An error occurred"


class DatabaseCluster:
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

    database_instance = None
    your_address = None
    friend_address = None
    bidirection = True

    @staticmethod
    @communication_server.on_event("startup")
    async def startup_event():
        DatabaseCluster.database_instance = CRDTGraph(bidirection=DatabaseCluster.bidirection)

        logger.info("Initialized CRDTGraph database instance!")
        logger.info(f"Communication server listening at {DatabaseCluster.your_address}")

        if DatabaseCluster.friend_address is not None:
            # let friend know you are connected to the network
            DatabaseCluster.database_instance.register_cluster_table(address=DatabaseCluster.friend_address)

            response = requests.post(f"{DatabaseCluster.friend_address}/register",
                                     data={"their_address": DatabaseCluster.your_address,
                                           "my_address": DatabaseCluster.your_address})
            response = response.json()["status"]

            logger.info(f"Register to {DatabaseCluster.friend_address}: {response}")

    @staticmethod
    def execute(host: str = "0.0.0.0", port: int = 8000, your_address=None, friend_address=None, bidirection=True):
        DatabaseCluster.bidirection = bidirection
        DatabaseCluster.your_address = your_address
        DatabaseCluster.friend_address = friend_address

        while host[-1] == "/":
            host = host[: -1]

        uvicorn.run(app=DatabaseCluster.communication_server, port=port, host=host)

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
        DatabaseCluster.database_instance.register_cluster_table(their_address)

        print(f"their_addr: {their_address}")
        print(f"my_addr: {DatabaseCluster.your_address}")
        print(f"cls_table: {DatabaseCluster.database_instance.get_cluster_table()}")

        for addr in DatabaseCluster.database_instance.get_cluster_table():
            if addr != their_address and addr != my_address:
                response = requests.post(f"{addr}/register",
                                         data={"their_address": their_address,
                                               "my_address": DatabaseCluster.your_address})
                response = response.json()["status"]
                logger.info(f"Broadcasted newcomer {their_address} to {addr}: {response}")

        return DatabaseCluster.response("Success", "Successfully register cluster address")

    @staticmethod
    @communication_server.get("/add_vertex/{u}")
    async def add_vertex(u: int):
        status, _ = DatabaseCluster.database_instance.add_vertex(u)
        return DatabaseCluster.response(status, f"Successfully added vertex {u}", error_msg=_)

    @staticmethod
    @communication_server.get("/add_edge/{u}/{v}")
    async def add_edge(u: int, v: int):
        status, _ = DatabaseCluster.database_instance.add_edge(u, v)
        return DatabaseCluster.response(status, f"Successfully added edge {u}-{v}", error_msg=_)

    @staticmethod
    @communication_server.get("/remove_vertex/{u}")
    async def remove_vertex(u: int):
        status = DatabaseCluster.database_instance.remove_vertex(u)
        return DatabaseCluster.response(status, f"Successfully removed vertex {u}")

    @staticmethod
    @communication_server.get("/remove_edge/{u}/{v}")
    async def remove_edge(u: int, v: int):
        status = DatabaseCluster.database_instance.remove_edge(u, v)
        return DatabaseCluster.response(status, f"Successfully removed edge {u}-{v}")

    @staticmethod
    @communication_server.get("/check_exists/{u}")
    async def exists_vertex(u: int):
        _, status = DatabaseCluster.database_instance.contains_vertex(u)
        return DatabaseCluster.response(_, data=status, success_msg=f"check_exists {u}: {status}")

    @staticmethod
    @communication_server.get("/check_exists/{u}/{v}")
    async def exists_edge(u: int, v: int):
        _, status = DatabaseCluster.database_instance.contains_edge(u, v)
        return DatabaseCluster.response(_, data=status, success_msg=f"check_exists {u}-{v}: {status}")

    @staticmethod
    @communication_server.get("/get_neighbors/{u}")
    async def get_neighbors(u: int):
        _, status = DatabaseCluster.database_instance.get_neighbors(u)
        return DatabaseCluster.response(_, data=status, success_msg=f"Successfully get neighbors of {status}")

    @staticmethod
    @communication_server.get("/find_path/{u}/{v}")
    async def find_path(u: int, v: int):
        status, path = DatabaseCluster.database_instance.find_path(u, v)
        return DatabaseCluster.response(status, data=path,
                                        success_msg=f"Successfully finding path from {u} to {v}: {path}",
                                        error_msg=f"Could not found path from {u} to {v}")

    @staticmethod
    @communication_server.get("/broadcast")
    async def broadcast():
        data = DatabaseCluster.database_instance.broadcast()

        # TODO: complete this
        for friend in DatabaseCluster.database_instance.get_cluster_table():
            response = requests.post(f"{friend}/merge", data=data)

        return DatabaseCluster.response("Success", data=data,
                                        success_msg="Successfully broadcast")

    @staticmethod
    @communication_server.get("/clear")
    async def clear():
        status = DatabaseCluster.database_instance.clear()
        return DatabaseCluster.response(status, data=status, success_msg="Successfully clear database")

    @staticmethod
    @communication_server.post("/merge")
    async def merge(vertices_added=Form(...),
                    vertices_removed=Form(...),
                    edges_added=Form(...),
                    edges_removed=Form(...)):
        print(vertices_added)
        print(vertices_removed)
        print(edges_added)
        print(edges_removed)
