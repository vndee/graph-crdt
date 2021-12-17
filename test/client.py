import unittest
from gcrdt_client import CRDTGraphClient


class CRDTGraphClientTestCase(unittest.TestCase):
    connection_string = "http://127.0.0.1:8000"

    def test_add_vertex(self):
        instance = CRDTGraphClient(CRDTGraphClientTestCase.connection_string)
        instance.clear()
        self.assertEqual(instance.add_vertex(1)["status"], "Success")
        self.assertEqual(instance.add_vertex(1)["status"], "Error")

    def test_remove_vertex(self):
        instance = CRDTGraphClient(CRDTGraphClientTestCase.connection_string)
        instance.clear()
        self.assertEqual(instance.add_vertex(1)["status"], "Success")
        self.assertEqual(instance.remove_vertex(1)["status"], "Success")
        self.assertEqual(instance.remove_vertex(1)["status"], "Error")

    def test_add_edge(self):
        instance = CRDTGraphClient(CRDTGraphClientTestCase.connection_string)
        instance.clear()
        self.assertEqual(instance.add_vertex(1)["status"], "Success")
        self.assertEqual(instance.add_vertex(2)["status"], "Success")
        self.assertEqual(instance.add_edge(1, 2)["status"], "Success")
        self.assertTrue(instance.exists_edge(1, 2))
        self.assertEqual(instance.add_edge(1, 2)["status"], "Error")
        print(instance.find_path(1, 2))


if __name__ == "__main__":
    unittest.main()
