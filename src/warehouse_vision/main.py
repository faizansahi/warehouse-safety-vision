import base64
import logging
from contextlib import asynccontextmanager
from dataclasses import asdict
from functools import lru_cache
from threading import Lock

import cv2
import numpy as np
from fastapi import FastAPI, File, HTTPException, Query, UploadFile
from sqlalchemy import select
from starlette.concurrency import run_in_threadpool

from .config import load_zones, settings
from .db import Base, SafetyEvent, Session, engine
from .domain import evaluate

LOG = logging.getLogger(__name__)
MODEL_LOCK = Lock()


@asynccontextmanager
async def lifespan(application: FastAPI):
    Base.metadata.create_all(engine)
    application.state.zones = load_zones(settings.zones_file)
    yield


app = FastAPI(title="Warehouse Safety Vision", version="0.1.0", lifespan=lifespan)


@lru_cache
def get_detector():
    from .detector import YoloDetector

    return YoloDetector(settings.yolo_weights, settings.confidence_threshold)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/events")
def events(limit: int = Query(default=100, ge=1, le=500)):
    with Session() as db:
        rows = db.scalars(
            select(SafetyEvent).order_by(SafetyEvent.occurred_at.desc()).limit(limit)
        ).all()
        return [
            {
                "id": row.id,
                "type": row.event_type,
                "severity": row.severity,
                "source": row.source,
                "details": row.details,
                "occurred_at": row.occurred_at,
            }
            for row in rows
        ]


def process_frame(frame: np.ndarray, filename: str) -> dict:
    try:
        with MODEL_LOCK:
            detections = get_detector().detect(frame)
    except Exception as exc:
        LOG.error("detector_unavailable error_type=%s", type(exc).__name__)
        with Session.begin() as db:
            db.add(
                SafetyEvent(
                    event_type="SYSTEM_ERROR",
                    severity="HIGH",
                    source=filename,
                    details={"error": "Detection model unavailable"},
                )
            )
        raise HTTPException(503, "Detection model unavailable") from exc
    zones = app.state.zones
    found = evaluate(detections, zones, settings.proximity_pixels)
    with Session.begin() as db:
        for event in found:
            db.add(
                SafetyEvent(
                    event_type=event["type"],
                    severity=event["severity"],
                    source=filename,
                    details={
                        key: value
                        for key, value in event.items()
                        if key not in {"type", "severity"}
                    },
                )
            )
    for zone in zones:
        polygon = np.array(zone.polygon, np.int32)
        cv2.polylines(frame, [polygon], True, (0, 165, 255), 2)
        cv2.putText(
            frame,
            zone.name,
            (10, frame.shape[0] - 15),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.6,
            (0, 165, 255),
            2,
        )
    for detection in detections:
        cv2.rectangle(frame, detection.box[:2], detection.box[2:], (0, 255, 0), 2)
        cv2.putText(
            frame,
            f"{detection.label} {detection.confidence:.2f}",
            (max(5, detection.box[0]), max(40, detection.box[1] - 8)),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.6,
            (0, 255, 0),
            2,
        )
    ok, encoded = cv2.imencode(".jpg", frame)
    if not ok:
        raise HTTPException(500, "Image encoding failed")
    LOG.info("frame_analyzed detections=%s events=%s", len(detections), len(found))
    return {
        "detections": len(detections),
        "detection_details": [asdict(item) for item in detections],
        "events": found,
        "annotated_jpeg_bytes": len(encoded),
        "annotated_jpeg_base64": base64.b64encode(encoded).decode(),
    }


@app.post("/analyze/frame")
async def analyze_frame(file: UploadFile = File(...)):
    data = await file.read(10_000_001)
    if len(data) > 10_000_000:
        raise HTTPException(413, "Image exceeds 10 MB")
    if not data:
        raise HTTPException(422, "Empty image")
    frame = cv2.imdecode(np.frombuffer(data, np.uint8), cv2.IMREAD_COLOR)
    if frame is None:
        raise HTTPException(422, "Invalid image")
    if frame.shape[0] * frame.shape[1] > 25_000_000:
        raise HTTPException(413, "Image exceeds 25 megapixels")
    return await run_in_threadpool(process_frame, frame, (file.filename or "upload")[:500])
