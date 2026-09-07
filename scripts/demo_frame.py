"""Run actual YOLO through the API; save its annotation and persisted events."""

import argparse
import base64
import hashlib
import json
from pathlib import Path

import httpx

SAMPLE_URL = (
    "https://raw.githubusercontent.com/scikit-image/scikit-image/v0.25.2/skimage/data/astronaut.png"
)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--base-url", default="http://127.0.0.1:8000")
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    images = root / "docs/images"
    output = root / "docs/results"
    images.mkdir(parents=True, exist_ok=True)
    output.mkdir(parents=True, exist_ok=True)
    sample = images / "sample.png"
    if not sample.exists():
        response = httpx.get(SAMPLE_URL, follow_redirects=True, timeout=60)
        response.raise_for_status()
        sample.write_bytes(response.content)
    with httpx.Client(base_url=args.base_url, timeout=300, trust_env=False) as api:
        response = api.post(
            "/analyze/frame",
            files={"file": ("nasa-astronaut.png", sample.read_bytes(), "image/png")},
        )
        response.raise_for_status()
        result = response.json()
        images.joinpath("demo.jpg").write_bytes(
            base64.b64decode(result.pop("annotated_jpeg_base64"))
        )
        events = api.get("/events")
        events.raise_for_status()
    result["persisted_events"] = events.json()
    result["sample_source"] = SAMPLE_URL
    result["sample_sha256"] = hashlib.sha256(sample.read_bytes()).hexdigest()
    result["note"] = (
        "NASA public-domain portrait with an illustrative configured zone; "
        "not a warehouse validation dataset."
    )
    assert result["detections"] > 0, (
        "No person detected; do not publish a successful detection claim"
    )
    (output / "demo.json").write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
