from unittest.mock import patch

from django.core.checks import run_checks
from django.test import SimpleTestCase, TestCase, override_settings

from tests.auth_tokens import EMAIL_CLAIM, foreign_key, issue_token, make_verifier

VERIFIER = "infrastructure.auth.drf_authentication.get_verifier"


@patch(VERIFIER, return_value=make_verifier())
class MeEndpointTests(TestCase):
    def get_me(self, token: str | None = None):
        headers = {"HTTP_AUTHORIZATION": f"Bearer {token}"} if token else {}
        return self.client.get("/api/me/", **headers)

    def test_returns_the_profile_for_a_valid_token(self, _) -> None:
        token = issue_token(sub="auth0|ana", **{EMAIL_CLAIM: "ana@example.com"})

        response = self.get_me(token)

        self.assertEqual(response.status_code, 200)
        body = response.json()
        self.assertEqual(body["subject"], "auth0|ana")
        self.assertEqual(body["email"], "ana@example.com")
        self.assertEqual(set(body), {"id", "subject", "email", "created_at"})

    def test_reuses_the_profile_on_later_requests(self, _) -> None:
        first = self.get_me(issue_token()).json()
        second = self.get_me(issue_token()).json()

        self.assertEqual(first["id"], second["id"])

    def test_401_without_a_token(self, _) -> None:
        response = self.get_me()

        self.assertEqual(response.status_code, 401)
        self.assertEqual(response["WWW-Authenticate"], 'Bearer realm="api"')

    def test_401_with_an_invalid_token(self, _) -> None:
        self.assertEqual(self.get_me(issue_token(key=foreign_key())).status_code, 401)

    def test_401_with_a_malformed_header(self, _) -> None:
        response = self.client.get("/api/me/", HTTP_AUTHORIZATION="Bearer a b")

        self.assertEqual(response.status_code, 401)

    def test_health_stays_public_even_with_a_bad_token(self, _) -> None:
        response = self.client.get("/api/health/", HTTP_AUTHORIZATION="Bearer junk")

        self.assertEqual(response.status_code, 200)


class SecuritySchemeTests(SimpleTestCase):
    def setUp(self) -> None:
        self.schema = self.client.get("/api/schema/", {"format": "json"}).json()

    def test_me_requires_the_bearer_scheme(self) -> None:
        security = self.schema["paths"]["/api/me/"]["get"]["security"]

        self.assertEqual(security, [{"Auth0Bearer": []}])
        self.assertEqual(
            self.schema["components"]["securitySchemes"]["Auth0Bearer"]["scheme"],
            "bearer",
        )

    def test_health_is_public(self) -> None:
        # `[{}]` (or no `security` key) is OpenAPI for "no credentials needed".
        operation = self.schema["paths"]["/api/health/"]["get"]

        self.assertEqual(operation.get("security", [{}]), [{}])


class Auth0SettingsCheckTests(SimpleTestCase):
    @override_settings(AUTH0_DOMAIN="", AUTH0_AUDIENCE="")
    def test_warns_when_auth0_is_not_configured(self) -> None:
        ids = [message.id for message in run_checks()]

        self.assertIn("auth.W001", ids)

    @override_settings(AUTH0_DOMAIN="tenant.test", AUTH0_AUDIENCE="https://api.test")
    def test_silent_when_configured(self) -> None:
        ids = [message.id for message in run_checks()]

        self.assertNotIn("auth.W001", ids)
