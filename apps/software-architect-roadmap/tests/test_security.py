import json
import secrets
import unittest
from architect_lab.security import (sign_token, verify_token, b64, pkce_challenge,
    AuthorizationCodes, password_record, check_password, encrypt_roundtrip)


class SecurityTests(unittest.TestCase):
    def setUp(self):
        self.key = secrets.token_bytes(32)
        self.claims = {"iss": "lab", "aud": "orders", "sub": "demo", "exp": 200, "iat": 100, "nbf": 100}

    def verify(self, token, now=100):
        return verify_token(token, self.key, issuer="lab", audience="orders", now=now)

    def test_valid_token(self):
        self.assertEqual(self.verify(sign_token(self.claims, self.key)), self.claims)

    def test_reject_expired_wrong_audience_issuer_future_and_missing_subject(self):
        for patch in [{"exp": 100}, {"aud": "other"}, {"iss": "other"}, {"nbf": 101}, {"iat": 101},
                      {"sub": ""}, {"exp": "200"}, {"exp": True}]:
            with self.subTest(patch=patch), self.assertRaises(ValueError):
                self.verify(sign_token({**self.claims, **patch}, self.key))

    def test_tampered_payload_and_none_algorithm(self):
        token = sign_token(self.claims, self.key)
        header, payload, signature = token.split('.')
        tampered = f"{header}.{b64(json.dumps({**self.claims, 'sub': 'admin'}).encode())}.{signature}"
        with self.assertRaises(ValueError): self.verify(tampered)
        with self.assertRaises(ValueError): self.verify(f"{b64(b'{\"alg\":\"none\"}')}.{payload}.{signature}")
        with self.assertRaises(ValueError): self.verify("broken")

    def test_pkce_rfc7636_vector(self):
        self.assertEqual(pkce_challenge('dBjftJeZ4CVP-mB92K27uhbUJU1p1r_wW1gFWFOEjXk'),
                         'E9Melhoa2OwvFrEMTJguCHaoeK1t8URWbuGJSstw-cM')

    def test_code_bound_to_client_redirect_verifier_and_one_use(self):
        codes = AuthorizationCodes()
        verifier = secrets.token_urlsafe(48)
        uri = 'http://127.0.0.1:8090/callback'
        code = codes.authorize('local-client', uri, pkce_challenge(verifier), 'demo', 100)
        for client, redirect, value, now in [('other', uri, verifier, 101), ('local-client', 'http://evil', verifier, 101),
             ('local-client', uri, secrets.token_urlsafe(48), 101), ('local-client', uri, verifier, 160)]:
            with self.subTest(client=client, now=now), self.assertRaises(ValueError):
                codes.exchange(code, client, redirect, value, now)
        self.assertEqual(codes.exchange(code, 'local-client', uri, verifier, 101)['sub'], 'demo')
        with self.assertRaises(ValueError): codes.exchange(code, 'local-client', uri, verifier, 102)

    def test_password_salt_and_wrong_password(self):
        one, two = password_record('example'), password_record('example')
        self.assertNotEqual(one, two)
        self.assertTrue(check_password('example', one))
        self.assertFalse(check_password('wrong', one))

    def test_authenticated_encryption(self):
        try:
            import cryptography
        except ImportError:
            self.skipTest('optional cryptography dependency is not installed')
        self.assertEqual(encrypt_roundtrip(), {'plaintext': 'order details', 'tamper_rejected': True})


if __name__ == '__main__': unittest.main()
