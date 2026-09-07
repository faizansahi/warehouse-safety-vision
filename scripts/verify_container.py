"""Verify a running container API using fictional/public fixtures."""

import base64
import json
import time
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE = "http://127.0.0.1:8000"
RECORDS = []


def request(method, path, payload=None, file=None):
    headers = {}
    content = None
    if payload is not None:
        content = json.dumps(payload).encode()
        headers["Content-Type"] = "application/json"
    if file:
        filename, media_type, data = file
        boundary = "portfolio-container-check"
        content = (
            (
                f'--{boundary}\r\nContent-Disposition: form-data; name="file"; '
                f'filename="{filename}"\r\nContent-Type: {media_type}\r\n\r\n'
            ).encode()
            + data
            + f"\r\n--{boundary}--\r\n".encode()
        )
        headers["Content-Type"] = f"multipart/form-data; boundary={boundary}"
    query = urllib.request.Request(BASE + path, data=content, headers=headers, method=method)
    with urllib.request.urlopen(query, timeout=300) as response:
        value = response.read()
        result = json.loads(value) if value else None
        RECORDS.append(
            {"method": method, "path": path, "status": response.status, "response": result}
        )
        return result


def main():
    for attempt in range(90):
        try:
            request("GET", "/health")
            break
        except (urllib.error.URLError, ConnectionError):
            if attempt == 89:
                raise
            time.sleep(1)
    result = request(
        "POST",
        "/analyze/frame",
        file=(
            "warehouse-source.jpg",
            "image/jpeg",
            (ROOT / "docs/images/warehouse-source.jpg").read_bytes(),
        ),
    )
    assert result["detections"] >= 1
    assert any(e["type"] == "PERSON_IN_RESTRICTED_ZONE" for e in result["events"])
    encoded = result.pop("annotated_jpeg_base64")
    output = ROOT / "docs/results/docker-frame.jpg"
    output.write_bytes(base64.b64decode(encoded))
    assert request("GET", "/events")[0]["type"] == "PERSON_IN_RESTRICTED_ZONE"
    output = ROOT / "docs/results/docker-demo.json"
    output.write_text(
        json.dumps({"database": "PostgreSQL 16 via Compose", "requests": RECORDS}, indent=2) + "\n",
        encoding="utf-8",
    )
    print("Container API workflow passed; output:", output.name)


if __name__ == "__main__":
    main()
