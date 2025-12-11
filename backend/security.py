import hmac
import hashlib
import json
from typing import Any, Dict

from .config import settings


def sign_payload(payload: Dict[str, Any]) -> str:
    body = json.dumps(payload, separators=(",", ":"), sort_keys=True).encode("utf-8")
    secret = settings.signing_secret.encode("utf-8")
    signature = hmac.new(secret, body, hashlib.sha256).hexdigest()
    return signature

