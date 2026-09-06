"""Security experiments. JWT and OAuth models are educational, not full providers."""
import base64
import hashlib
import hmac
import json
import math
import re
import secrets


def b64(raw):
    return base64.urlsafe_b64encode(raw).rstrip(b"=").decode("ascii")


def unb64(text):
    if not isinstance(text, str) or not re.fullmatch(r"[A-Za-z0-9_-]+", text):
        raise ValueError("invalid base64url")
    return base64.b64decode(text + "=" * (-len(text) % 4), altchars=b"-_", validate=True)


def sign_token(claims, key):
    if len(key) < 32:
        raise ValueError("use at least 256 bits of random key material")
    header = b64(b'{"alg":"HS256","typ":"JWT"}')
    body = b64(json.dumps(claims, separators=(",", ":"), allow_nan=False).encode())
    message = f"{header}.{body}"
    return message + "." + b64(hmac.digest(key, message.encode(), "sha256"))


def verify_token(token, key, *, issuer, audience, now):
    if len(key) < 32 or not isinstance(token, str) or len(token) > 8192:
        raise ValueError("invalid token or key")
    try:
        header, payload, signature = token.split(".")
        if json.loads(unb64(header)) != {"alg": "HS256", "typ": "JWT"}:
            raise ValueError("unsupported token header")
        expected = hmac.digest(key, f"{header}.{payload}".encode(), "sha256")
        if not hmac.compare_digest(expected, unb64(signature)):
            raise ValueError("invalid signature")
        claims = json.loads(unb64(payload))
        if not isinstance(claims, dict):
            raise ValueError("claims must be an object")
        for field in ("exp", "iat", "nbf"):
            if field in claims:
                value = claims[field]
                if type(value) not in (int, float) or not math.isfinite(value):
                    raise ValueError("invalid numeric date")
        if "exp" not in claims or now >= claims["exp"]:
            raise ValueError("expired or missing expiry")
        if now < claims.get("nbf", now) or now < claims.get("iat", now):
            raise ValueError("token not active")
        if claims.get("iss") != issuer or claims.get("aud") != audience:
            raise ValueError("invalid issuer or audience")
        if not isinstance(claims.get("sub"), str) or not claims["sub"]:
            raise ValueError("subject required")
        return claims
    except (TypeError, KeyError, UnicodeError, OverflowError, json.JSONDecodeError) as error:
        raise ValueError("malformed token") from error


def pkce_challenge(verifier):
    if not isinstance(verifier, str) or not re.fullmatch(r"[A-Za-z0-9._~-]{43,128}", verifier):
        raise ValueError("invalid PKCE verifier")
    return b64(hashlib.sha256(verifier.encode("ascii")).digest())


class AuthorizationCodes:
    """Models code binding and replay prevention after user authentication/consent."""
    def __init__(self):
        self.codes = {}

    def authorize(self, client_id, redirect_uri, challenge, subject, now):
        if client_id != "local-client" or redirect_uri != "http://127.0.0.1:8090/callback":
            raise ValueError("unregistered client or redirect URI")
        if not re.fullmatch(r"[A-Za-z0-9_-]{43}", challenge):
            raise ValueError("S256 challenge required")
        code = secrets.token_urlsafe(32)
        self.codes[code] = (client_id, redirect_uri, challenge, subject, now + 60)
        return code

    def exchange(self, code, client_id, redirect_uri, verifier, now):
        record = self.codes.get(code)
        if not record:
            raise ValueError("unknown or used code")
        client, redirect, challenge, subject, expiry = record
        if client_id != client or redirect_uri != redirect or now >= expiry:
            raise ValueError("invalid code binding or expired code")
        if not hmac.compare_digest(challenge, pkce_challenge(verifier)):
            raise ValueError("PKCE verification failed")
        del self.codes[code]
        return {"sub": subject, "scope": "orders:read"}


def password_record(password):
    salt = secrets.token_bytes(16)
    digest = hashlib.scrypt(password.encode(), salt=salt, n=2**14, r=8, p=1)
    return {"salt": salt.hex(), "digest": digest.hex()}


def check_password(password, record):
    digest = hashlib.scrypt(password.encode(), salt=bytes.fromhex(record["salt"]), n=2**14, r=8, p=1)
    return hmac.compare_digest(digest.hex(), record["digest"])


def encrypt_roundtrip():
    from cryptography.hazmat.primitives.ciphers.aead import AESGCM
    from cryptography.exceptions import InvalidTag
    cipher = AESGCM(AESGCM.generate_key(bit_length=256))
    nonce = secrets.token_bytes(12)
    ciphertext = cipher.encrypt(nonce, b"order details", b"order:42")
    plaintext = cipher.decrypt(nonce, ciphertext, b"order:42")
    try:
        cipher.decrypt(nonce, ciphertext, b"order:43")
    except InvalidTag:
        tamper_rejected = True
    else:
        tamper_rejected = False
    return {"plaintext": plaintext.decode(), "tamper_rejected": tamper_rejected}
