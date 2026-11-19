import time
from unittest import TestCase

from application.auth.ports import InvalidAccessToken
from infrastructure.auth.jwt_verifier import UnconfiguredVerifier
from tests.auth_tokens import EMAIL_CLAIM, foreign_key, issue_token, make_verifier


class JwtAccessTokenVerifierTests(TestCase):
    def setUp(self) -> None:
        self.verifier = make_verifier()

    def assertRejected(self, token: str) -> None:
        with self.assertRaises(InvalidAccessToken):
            self.verifier.verify(token)

    def test_accepts_a_valid_token(self) -> None:
        identity = self.verifier.verify(issue_token(sub="auth0|ana"))

        self.assertEqual(identity.subject, "auth0|ana")
        self.assertIsNone(identity.email)

    def test_reads_the_email_from_the_namespaced_claim(self) -> None:
        token = issue_token(**{EMAIL_CLAIM: "ana@example.com"})

        self.assertEqual(self.verifier.verify(token).email, "ana@example.com")

    def test_accepts_an_audience_list_that_includes_ours(self) -> None:
        token = issue_token(aud=["https://api.test", "https://tenant.test/userinfo"])

        self.assertEqual(self.verifier.verify(token).subject, "auth0|ana")

    def test_rejects_an_expired_token(self) -> None:
        self.assertRejected(issue_token(exp=int(time.time()) - 60))

    def test_rejects_another_audience(self) -> None:
        self.assertRejected(issue_token(aud="https://someone-else.test"))

    def test_rejects_another_issuer(self) -> None:
        self.assertRejected(issue_token(iss="https://evil.test/"))

    def test_rejects_a_token_without_subject(self) -> None:
        self.assertRejected(issue_token(sub=None))

    def test_rejects_a_token_without_expiry(self) -> None:
        self.assertRejected(issue_token(exp=None))

    def test_rejects_a_token_signed_by_another_key(self) -> None:
        self.assertRejected(issue_token(key=foreign_key()))

    def test_rejects_hs256(self) -> None:
        self.assertRejected(
            issue_token(key="a-shared-secret-that-is-long-enough!", algorithm="HS256")
        )

    def test_rejects_alg_none(self) -> None:
        self.assertRejected(issue_token(key=None, algorithm="none"))

    def test_rejects_garbage(self) -> None:
        self.assertRejected("not-a-jwt")


class UnconfiguredVerifierTests(TestCase):
    def test_rejects_everything(self) -> None:
        with self.assertRaises(InvalidAccessToken):
            UnconfiguredVerifier().verify(issue_token())
