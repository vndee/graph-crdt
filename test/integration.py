import unittest
from gcrdt_client import CRDTGraphClient


class CRDTGraphIntegrationTestCase(unittest.TestCase):
    cluster_1 = "http://127.0.0.1:8081"
    cluster_2 = "http://127.0.0.1:8082"
    cluster_3 = "http://127.0.0.1:8083"
    cluster_4 = "http://127.0.0.1:8084"
    cluster_5 = "http://127.0.0.1:8085"

    def test_add_vertex(self):
        instance_1 = CRDTGraphClient(CRDTGraphIntegrationTestCase.cluster_1)
        instance_2 = CRDTGraphClient(CRDTGraphIntegrationTestCase.cluster_2)
        instance_3 = CRDTGraphClient(CRDTGraphIntegrationTestCase.cluster_3)
        instance_4 = CRDTGraphClient(CRDTGraphIntegrationTestCase.cluster_4)
        instance_5 = CRDTGraphClient(CRDTGraphIntegrationTestCase.cluster_5)

        self.assertTrue(instance_1.clear())
        self.assertEqual(instance_1.broadcast(), "Success")

        self.assertEqual(instance_1.add_vertex(1)["status"], "Success")
        self.assertEqual(instance_1.broadcast(), "Success")
        self.assertTrue(instance_1.exists_vertex(1))
        self.assertTrue(instance_2.exists_vertex(1))
        self.assertTrue(instance_3.exists_vertex(1))
        self.assertTrue(instance_4.exists_vertex(1))
        self.assertTrue(instance_5.exists_vertex(1))

    def test_remove_vertex(self):
        instance_1 = CRDTGraphClient(CRDTGraphIntegrationTestCase.cluster_1)
        instance_2 = CRDTGraphClient(CRDTGraphIntegrationTestCase.cluster_2)
        instance_3 = CRDTGraphClient(CRDTGraphIntegrationTestCase.cluster_3)
        instance_4 = CRDTGraphClient(CRDTGraphIntegrationTestCase.cluster_4)
        instance_5 = CRDTGraphClient(CRDTGraphIntegrationTestCase.cluster_5)

        self.assertTrue(instance_1.clear())
        self.assertEqual(instance_1.broadcast(), "Success")

        self.assertEqual(instance_1.add_vertex(1)["status"], "Success")
        self.assertEqual(instance_1.broadcast(), "Success")
        self.assertEqual(instance_5.remove_vertex(1)["status"], "Success")
        self.assertEqual(instance_5.broadcast(), "Success")
        self.assertFalse(instance_1.exists_vertex(1))
        self.assertFalse(instance_2.exists_vertex(1))
        self.assertFalse(instance_3.exists_vertex(1))
        self.assertFalse(instance_4.exists_vertex(1))
        self.assertFalse(instance_5.exists_vertex(1))

    def test_add_edge(self):
        instance_1 = CRDTGraphClient(CRDTGraphIntegrationTestCase.cluster_1)
        instance_2 = CRDTGraphClient(CRDTGraphIntegrationTestCase.cluster_2)
        instance_3 = CRDTGraphClient(CRDTGraphIntegrationTestCase.cluster_3)
        instance_4 = CRDTGraphClient(CRDTGraphIntegrationTestCase.cluster_4)
        instance_5 = CRDTGraphClient(CRDTGraphIntegrationTestCase.cluster_5)

        self.assertTrue(instance_1.clear())
        self.assertEqual(instance_1.broadcast(), "Success")

        self.assertEqual(instance_1.add_vertex(1)["status"], "Success")
        self.assertEqual(instance_2.add_vertex(2)["status"], "Success")
        self.assertEqual(instance_1.broadcast(), "Success")
        self.assertEqual(instance_2.broadcast(), "Success")
        self.assertEqual(instance_3.add_edge(1, 2)["status"], "Success")
        self.assertEqual(instance_3.broadcast(), "Success")

        self.assertTrue(instance_1.exists_edge(1, 2))
        self.assertTrue(instance_2.exists_edge(1, 2))
        self.assertTrue(instance_3.exists_edge(1, 2))
        self.assertTrue(instance_4.exists_edge(1, 2))
        self.assertTrue(instance_5.exists_edge(1, 2))

    def test_remove_edge(self):
        instance_1 = CRDTGraphClient(CRDTGraphIntegrationTestCase.cluster_1)
        instance_2 = CRDTGraphClient(CRDTGraphIntegrationTestCase.cluster_2)
        instance_3 = CRDTGraphClient(CRDTGraphIntegrationTestCase.cluster_3)
        instance_4 = CRDTGraphClient(CRDTGraphIntegrationTestCase.cluster_4)
        instance_5 = CRDTGraphClient(CRDTGraphIntegrationTestCase.cluster_5)

        self.assertTrue(instance_1.clear())
        self.assertEqual(instance_1.broadcast(), "Success")

        self.assertEqual(instance_1.add_vertex(1)["status"], "Success")
        self.assertEqual(instance_2.add_vertex(2)["status"], "Success")
        self.assertEqual(instance_1.broadcast(), "Success")
        self.assertEqual(instance_2.broadcast(), "Success")
        self.assertEqual(instance_3.add_edge(1, 2)["status"], "Success")
        self.assertEqual(instance_3.broadcast(), "Success")

        self.assertTrue(instance_1.exists_edge(1, 2))
        self.assertTrue(instance_2.exists_edge(1, 2))
        self.assertTrue(instance_3.exists_edge(1, 2))
        self.assertTrue(instance_4.exists_edge(1, 2))
        self.assertTrue(instance_5.exists_edge(1, 2))

        self.assertEqual(instance_1.remove_edge(1, 2)["status"], "Success")
        self.assertEqual(instance_1.broadcast(), "Success")

        self.assertFalse(instance_1.exists_edge(1, 2))
        self.assertFalse(instance_2.exists_edge(1, 2))
        self.assertFalse(instance_3.exists_edge(1, 2))
        self.assertFalse(instance_4.exists_edge(1, 2))
        self.assertFalse(instance_5.exists_edge(1, 2))

    def test_get_neighbors_and_find_paths(self):
        instance_1 = CRDTGraphClient(CRDTGraphIntegrationTestCase.cluster_1)
        instance_2 = CRDTGraphClient(CRDTGraphIntegrationTestCase.cluster_2)
        instance_3 = CRDTGraphClient(CRDTGraphIntegrationTestCase.cluster_3)
        instance_4 = CRDTGraphClient(CRDTGraphIntegrationTestCase.cluster_4)
        instance_5 = CRDTGraphClient(CRDTGraphIntegrationTestCase.cluster_5)

        self.assertTrue(instance_1.clear())
        self.assertEqual(instance_1.broadcast(), "Success")

        self.assertEqual(instance_1.add_vertex(1)["status"], "Success")
        self.assertEqual(instance_2.add_vertex(2)["status"], "Success")
        self.assertEqual(instance_3.add_vertex(3)["status"], "Success")

        self.assertEqual(instance_1.broadcast(), "Success")
        self.assertEqual(instance_2.broadcast(), "Success")
        self.assertEqual(instance_3.broadcast(), "Success")

        self.assertEqual(instance_1.add_edge(1, 2)["status"], "Success")
        self.assertEqual(instance_1.broadcast(), "Success")

        self.assertEqual(instance_2.find_path(1, 2)["data"], [1, 2])
        self.assertEqual(instance_3.add_edge(1, 3)["status"], "Success")
        self.assertEqual(instance_3.broadcast(), "Success")

        self.assertEqual(instance_4.find_path(2, 3)["data"], [2, 1, 3])
        self.assertEqual(instance_5.get_neighbors(1), [2, 3])
        self.assertEqual(instance_5.add_vertex(4)["status"], "Success")
        self.assertEqual(instance_5.broadcast(), "Success")

        self.assertEqual(instance_1.find_path(1, 4)["status"], "Error")


if __name__ == "__main__":
    unittest.main()
