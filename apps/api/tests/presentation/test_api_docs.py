from django.test import SimpleTestCase


class ApiDocsTests(SimpleTestCase):
    def test_schema_lists_the_health_endpoint(self) -> None:
        response = self.client.get("/api/schema/", {"format": "json"})

        self.assertEqual(response.status_code, 200)
        self.assertIn("/api/health/", response.json()["paths"])

    def test_swagger_ui_is_served(self) -> None:
        response = self.client.get("/api/docs/")

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "swagger-ui")
