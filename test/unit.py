import unittest
from gcrdt_client import CRDTGraphClient


class CRDTGraphClientTestCase(unittest.TestCase):
    connection_string = "http://127.0.0.1:8081"

    def test_add_vertex(self):
        instance = CRDTGraphClient(CRDTGraphClientTestCase.connection_string)
        self.assertTrue(instance.clear())
        self.assertEqual(instance.add_vertex(1)["status"], "Success")
        self.assertEqual(instance.add_vertex(1)["status"], "Error")

    def test_exists_vertex(self):
        instance = CRDTGraphClient(CRDTGraphClientTestCase.connection_string)
        self.assertTrue(instance.clear())
        self.assertEqual(instance.add_vertex(1)["status"], "Success")
        self.assertEqual(instance.add_vertex(1)["status"], "Error")
        self.assertTrue(instance.exists_vertex(1))

    def test_remove_vertex(self):
        instance = CRDTGraphClient(CRDTGraphClientTestCase.connection_string)
        self.assertTrue(instance.clear())
        self.assertEqual(instance.add_vertex(1)["status"], "Success")
        self.assertEqual(instance.remove_vertex(1)["status"], "Success")
        self.assertEqual(instance.remove_vertex(1)["status"], "Error")

    def test_add_edge(self):
        instance = CRDTGraphClient(CRDTGraphClientTestCase.connection_string)
        self.assertTrue(instance.clear())
        self.assertEqual(instance.add_vertex(1)["status"], "Success")
        self.assertEqual(instance.add_vertex(2)["status"], "Success")
        self.assertEqual(instance.add_edge(1, 2)["status"], "Success")
        self.assertTrue(instance.exists_edge(1, 2))
        self.assertEqual(instance.add_edge(1, 2)["status"], "Error")

    def test_exists_edge(self):
        instance = CRDTGraphClient(CRDTGraphClientTestCase.connection_string)
        self.assertTrue(instance.clear())
        self.assertEqual(instance.add_vertex(1)["status"], "Success")
        self.assertEqual(instance.add_vertex(2)["status"], "Success")
        self.assertEqual(instance.add_edge(1, 2)["status"], "Success")
        self.assertTrue(instance.exists_edge(1, 2))

    def test_remove_edge(self):
        instance = CRDTGraphClient(CRDTGraphClientTestCase.connection_string)
        self.assertTrue(instance.clear())
        self.assertEqual(instance.add_vertex(1)["status"], "Success")
        self.assertEqual(instance.add_vertex(2)["status"], "Success")
        self.assertEqual(instance.add_edge(1, 2)["status"], "Success")
        self.assertTrue(instance.exists_edge(1, 2))
        self.assertEqual(instance.remove_edge(1, 2)["status"], "Success")
        self.assertFalse(instance.exists_edge(1, 2))

    def test_find_path(self):
        instance = CRDTGraphClient(CRDTGraphClientTestCase.connection_string)
        self.assertTrue(instance.clear())
        self.assertEqual(instance.add_vertex(1)["status"], "Success")
        self.assertEqual(instance.add_vertex(2)["status"], "Success")
        self.assertEqual(instance.add_vertex(3)["status"], "Success")
        self.assertEqual(instance.add_edge(1, 2)["status"], "Success")
        self.assertEqual(instance.find_path(1, 2)["data"], [1, 2])
        self.assertEqual(instance.add_edge(1, 3)["status"], "Success")
        self.assertEqual(instance.find_path(2, 3)["data"], [2, 1, 3])

    def test_get_neighbors(self):
        instance = CRDTGraphClient(CRDTGraphClientTestCase.connection_string)
        self.assertTrue(instance.clear())
        self.assertEqual(instance.add_vertex(1)["status"], "Success")
        self.assertEqual(instance.add_vertex(2)["status"], "Success")
        self.assertEqual(instance.add_vertex(3)["status"], "Success")
        self.assertEqual(instance.add_edge(1, 2)["status"], "Success")
        self.assertEqual(instance.find_path(1, 2)["data"], [1, 2])
        self.assertEqual(instance.add_edge(1, 3)["status"], "Success")
        self.assertEqual(instance.find_path(2, 3)["data"], [2, 1, 3])
        self.assertEqual(instance.get_neighbors(1), [2, 3])
        self.assertEqual(instance.add_vertex(4)["status"], "Success")
        self.assertEqual(instance.find_path(1, 4)["status"], "Error")

    # def test_monodirection(self):
    #     instance = CRDTGraphClient(CRDTGraphClientTestCase.connection_string)
    #     self.assertTrue(instance.clear())
    #     self.assertEqual(instance.add_vertex(1)["status"], "Success")
    #     self.assertEqual(instance.add_vertex(2)["status"], "Success")
    #     self.assertEqual(instance.add_edge(1, 2)["status"], "Success")
    #     self.assertTrue(instance.exists_edge(1, 2))
    #     self.assertFalse(instance.exists_edge(2, 1))


if __name__ == "__main__":
    unittest.main()
