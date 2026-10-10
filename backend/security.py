import base64
import hashlib
import json
from cryptography.fernet import Fernet, InvalidToken


def _fernet(secret):
    key = base64.urlsafe_b64encode(hashlib.sha256(secret.encode("utf-8")).digest())
    return Fernet(key)


def seal(payload, secret):
    return _fernet(secret).encrypt(json.dumps(payload, separators=(",", ":")).encode()).decode()


def unseal(token, secret):
    try:
        return json.loads(_fernet(secret).decrypt(token.encode(), ttl=60 * 60 * 8))
    except (InvalidToken, ValueError, TypeError, json.JSONDecodeError):
        return None
