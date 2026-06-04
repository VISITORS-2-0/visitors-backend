import unittest
from fastapi.testclient import TestClient
from app.main import app

class ConceptsEndpointTests(unittest.TestCase):
    def setUp(self):
        # We need to initialize the entities as the startup event does.
        # But wait, app.dependency_overrides could be used if needed, 
        # or we just rely on startup event or initialize it manually.
        from app.services.concept_manager import concept_manager_instance
        concept_manager_instance.init_entities()
        self.client = TestClient(app)

    def test_get_concept_values(self):
        response = self.client.get("/api/v1/concept/concept-values")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        
        self.assertIsInstance(data, dict)
        self.assertIn("ALP", data)
        self.assertIn("min", data["ALP"])
        self.assertIn("max", data["ALP"])
        
        # Test a nominal concept or a pattern with values
        self.assertIn("Sex", data)
        self.assertIn("values", data["Sex"])
        self.assertEqual(data["Sex"]["values"], ["1", "2"])

if __name__ == "__main__":
    unittest.main()
