"""Run actual YOLO through the API; save its annotation and persisted events."""

import argparse
import base64
import hashlib
import html
import json
from pathlib import Path

import httpx

SAMPLE_URL = "https://d1ldvf68ux039x.cloudfront.net/thumbs/photos/2310/8052998/1000w_q95.jpg"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--base-url", default="http://127.0.0.1:8000")
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    images = root / "docs/images"
    output = root / "docs/results"
    images.mkdir(parents=True, exist_ok=True)
    output.mkdir(parents=True, exist_ok=True)
    sample = images / "warehouse-source.jpg"
    if not sample.exists():
        response = httpx.get(SAMPLE_URL, follow_redirects=True, timeout=60)
        response.raise_for_status()
        sample.write_bytes(response.content)
    with httpx.Client(base_url=args.base_url, timeout=300, trust_env=False) as api:
        response = api.post(
            "/analyze/frame",
            files={"file": (sample.name, sample.read_bytes(), "image/jpeg")},
        )
        response.raise_for_status()
        result = response.json()
        images.joinpath("safety-zone-alert.jpg").write_bytes(
            base64.b64decode(result.pop("annotated_jpeg_base64"))
        )
        events = api.get("/events")
        events.raise_for_status()
    result["persisted_events"] = events.json()
    result["sample_source"] = SAMPLE_URL
    result["sample_sha256"] = hashlib.sha256(sample.read_bytes()).hexdigest()
    result["note"] = (
        "DVIDS warehouse photograph by Ricardo J. Reyes, photo 8052998. "
        "The configured zone is a demonstration, not an assessment of the photographed worker."
    )
    assert result["detections"] > 0, (
        "No person detected; do not publish a successful detection claim"
    )
    assert any(event["type"] == "PERSON_IN_RESTRICTED_ZONE" for event in result["events"])
    from ultralytics import YOLO

    from warehouse_vision.config import settings

    prediction = YOLO(settings.yolo_weights)(sample, conf=settings.confidence_threshold)[0]
    prediction.save(filename=str(images / "person-detection.jpg"))
    (output / "demo.json").write_text(json.dumps(result, indent=2) + "\n")
    event_json = html.escape(json.dumps(result["persisted_events"], indent=2))
    report = f"""<!doctype html><html lang="en"><meta charset="utf-8">
    <title>Recorded safety events</title>
    <style>body{{font:18px/1.5 system-ui;margin:40px;color:#172b3a}}
    pre{{font:16px/1.5 monospace;background:#f1f6f8;padding:24px;white-space:pre-wrap}}</style>
    <h1>GET /events</h1><p>Actual SQLite event API response after warehouse image inference.</p>
    <pre>{event_json}</pre><p>The exclusion zone is a demo configuration,
    not a finding about the photographed worker.</p></html>"""
    (output / "events.html").write_text(report, encoding="utf-8")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
