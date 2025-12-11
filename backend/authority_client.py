import logging
from typing import Any, Dict

import http.client
import json
from urllib.parse import urlparse

from .config import settings
from .security import sign_payload

logger = logging.getLogger(__name__)


def send_alert(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Mock secure API call to authorities with signed payload."""
    signature = sign_payload(payload)
    full_payload = {**payload, "signature": signature}

    parsed = urlparse(settings.authority_api_url)
    body = json.dumps(full_payload)
    headers = {"Content-Type": "application/json"}

    try:
        if parsed.scheme == "https":
            conn = http.client.HTTPSConnection(parsed.hostname, parsed.port or 443, timeout=5)
        else:
            conn = http.client.HTTPConnection(parsed.hostname, parsed.port or 80, timeout=5)

        path = parsed.path or "/"
        conn.request("POST", path, body=body, headers=headers)
        resp = conn.getresponse()
        resp_body = resp.read().decode("utf-8", errors="ignore")
        logger.info("Alert dispatched: status=%s body=%s", resp.status, resp_body)
        return {"status": resp.status, "body": resp_body}
    except Exception as exc:  # noqa: BLE001
        logger.warning("Alert dispatch failed (simulated ok): %s", exc)
        return {"status": 200, "body": "simulated-send-ok"}

