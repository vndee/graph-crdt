import uvicorn
from fastapi import FastAPI
from graph_crdt import CRDTGraph
from fastapi.middleware.cors import CORSMiddleware


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

    database_instance = CRDTGraph()

    @staticmethod
    def execute(host: str = "0.0.0.0", port: int = 8000):
        uvicorn.run(app=DatabaseCluster.communication_server, port=port, host=host)

    @staticmethod
    def response(status, success_msg, data="", error_msg=ResponseStatus.error_default_msg):
        if status:
            return {
                "status": ResponseStatus.success,
                "data": data,
                "message": success_msg
            }
        else:
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
    @communication_server.get("/add_vertex/{u}")
    async def add_vertex(u: int):
        status = DatabaseCluster.database_instance.add_vertex(u)
        DatabaseCluster.response(status, f"Successfully added vertex {u}")

    @staticmethod
    @communication_server.get("/add_edge/{u}/{v}")
    async def add_edge(u: int, v: int):
        status = DatabaseCluster.database_instance.add_edge(u, v)
        DatabaseCluster.response(status, f"Successfully added edge {u}-{v}")

    @staticmethod
    @communication_server.get("/remove_vertex/{u}")
    async def remove_vertex(u: int):
        status = DatabaseCluster.database_instance.remove_vertex(u)
        DatabaseCluster.response(status, f"Successfully removed vertex {u}")

    @staticmethod
    @communication_server.get("/remove_edge/{u}/{v}")
    async def remove_edge(u: int, v: int):
        status = DatabaseCluster.database_instance.remove_edge(u, v)
        DatabaseCluster.response(status, f"Successfully removed edge {u}-{v}")

    @staticmethod
    @communication_server.get("/check_exists/{u}")
    async def exists_vertex(u: int):
        _, status = DatabaseCluster.database_instance.contains_vertex(u)
        DatabaseCluster.response(_, data=status, success_msg="")

    @staticmethod
    @communication_server.get("/check_exists/{u}/{v}")
    async def exists_edge(u: int, v: int):
        _, status = DatabaseCluster.database_instance.contains_edge(u, v)
        DatabaseCluster.response(_, data=status, success_msg="")
