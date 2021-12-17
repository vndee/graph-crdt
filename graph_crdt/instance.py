import uvicorn
from fastapi import FastAPI
from graph_crdt import CRDTGraph
from fastapi.middleware.cors import CORSMiddleware


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
    @communication_server.get("/")
    async def status():
        return {
            "message": "OK!"
        }

    @staticmethod
    @communication_server.get("/add_vertex/{u}")
    async def add_vertex(u: int):
        status = DatabaseCluster.database_instance.add_vertex(u)
        if status is True:
            return {
                "status": "Success",
                "message": f"Successfully added vertex {u}"
            }
        else:
            return {
                "status": "Error",
                "message": f"An error occurred"
            }
