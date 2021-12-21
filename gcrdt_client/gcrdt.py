import requests


class CRDTGraphClient:
    def __init__(self, host: str):
        while host[-1] == "/":
            host = host[: -1]

        self.host = host

    def add_vertex(self, u):
        response = requests.get(f"{self.host}/add_vertex/{u}")
        return response.json()

    def add_edge(self, u, v):
        response = requests.get(f"{self.host}/add_edge/{u}/{v}")
        return response.json()

    def remove_vertex(self, u):
        response = requests.get(f"{self.host}/remove_vertex/{u}")
        return response.json()

    def remove_edge(self, u, v):
        response = requests.get(f"{self.host}/remove_edge/{u}/{v}")
        return response.json()

    def exists_vertex(self, u):
        response = requests.get(f"{self.host}/check_exists/{u}")
        return response.json()["data"]

    def exists_edge(self, u, v):
        response = requests.get(f"{self.host}/check_exists/{u}/{v}")
        return response.json()["data"]

    def find_path(self, u, v):
        response = requests.get(f"{self.host}/find_path/{u}/{v}")
        return response.json()

    def get_neighbors(self, u):
        response = requests.get(f"{self.host}/get_neighbors/{u}")
        return response.json()["data"]

    def clear(self):
        response = requests.get(f"{self.host}/clear")
        return response.json()["data"]

    def broadcast(self):
        response = requests.get(f"{self.host}/broadcast")
        return response.json()["status"]
