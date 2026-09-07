"""Send video frames to the running event API and save real annotations."""

import argparse
import base64
from pathlib import Path

import cv2
import httpx


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("source", help="Video path, webcam index, or RTSP URL")
    parser.add_argument("--base-url", default="http://127.0.0.1:8000")
    parser.add_argument("--output", default="outputs")
    parser.add_argument("--every", type=int, default=30)
    args = parser.parse_args()
    if args.every < 1:
        parser.error("--every must be positive")
    source = int(args.source) if args.source.isdigit() else args.source
    capture = cv2.VideoCapture(source)
    if not capture.isOpened():
        raise RuntimeError("Unable to open video source")
    destination = Path(args.output)
    destination.mkdir(parents=True, exist_ok=True)
    index = 0
    try:
        with httpx.Client(base_url=args.base_url, timeout=300, trust_env=False) as api:
            while True:
                ok, frame = capture.read()
                if not ok:
                    break
                if index % args.every == 0:
                    encoded_ok, encoded = cv2.imencode(".jpg", frame)
                    if not encoded_ok:
                        raise RuntimeError("Frame encoding failed")
                    response = api.post(
                        "/analyze/frame",
                        files={"file": (f"frame-{index}.jpg", encoded.tobytes(), "image/jpeg")},
                    )
                    response.raise_for_status()
                    destination.joinpath(f"frame-{index:06d}.jpg").write_bytes(
                        base64.b64decode(response.json()["annotated_jpeg_base64"])
                    )
                index += 1
    finally:
        capture.release()


if __name__ == "__main__":
    main()
