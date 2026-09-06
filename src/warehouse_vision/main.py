import base64
import os

import cv2
import numpy as np
from fastapi import FastAPI, File, HTTPException, UploadFile
from sqlalchemy import select

from .db import Base, SafetyEvent, Session, engine
from .domain import Zone, ZoneKind, evaluate

app = FastAPI(title="Warehouse Safety Vision", version="0.1.0")
Base.metadata.create_all(engine)
ZONES = [Zone("loading-bay", ZoneKind.RESTRICTED, [(0, 0), (400, 0), (400, 300), (0, 300)])]


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/events")
def events(limit: int = 100):
    with Session() as db:
        rows = db.scalars(
            select(SafetyEvent).order_by(SafetyEvent.occurred_at.desc()).limit(min(limit, 500))
        ).all()
        return [
            {
                "id": r.id,
                "type": r.event_type,
                "severity": r.severity,
                "source": r.source,
                "details": r.details,
                "occurred_at": r.occurred_at,
            }
            for r in rows
        ]


@app.post("/analyze/frame")
async def analyze_frame(file: UploadFile = File(...)):
    data = await file.read()
    frame = cv2.imdecode(np.frombuffer(data, np.uint8), cv2.IMREAD_COLOR)
    if frame is None:
        raise HTTPException(422, "Invalid image")
    # Endpoint accepts explicit detector activation to avoid hidden model downloads in API startup.
    from .detector import YoloDetector

    try:
        detections = YoloDetector(
            os.getenv("YOLO_WEIGHTS", "yolo11n.pt"),
            float(os.getenv("CONFIDENCE_THRESHOLD", "0.4")),
        ).detect(frame)
    except Exception as exc:
        with Session.begin() as db:
            db.add(
                SafetyEvent(
                    event_type="SYSTEM_ERROR",
                    severity="HIGH",
                    source=file.filename or "upload",
                    details={"error": str(exc)[:500]},
                )
            )
        raise HTTPException(503, "Detection model unavailable") from exc
    found = evaluate(detections, ZONES, float(os.getenv("PROXIMITY_PIXELS", "120")))
    with Session.begin() as db:
        for event in found:
            db.add(
                SafetyEvent(
                    event_type=event["type"],
                    severity=event["severity"],
                    source=file.filename or "upload",
                    details={k: v for k, v in event.items() if k not in {"type", "severity"}},
                )
            )
    for detection in detections:
        cv2.rectangle(frame, detection.box[:2], detection.box[2:], (0, 255, 0), 2)
    ok, encoded = cv2.imencode(".jpg", frame)
    return {
        "detections": len(detections),
        "events": [
            {k: str(v) if k in {"type", "severity"} else v for k, v in e.items()} for e in found
        ],
        "annotated_jpeg_bytes": len(encoded) if ok else 0,
        "annotated_jpeg_base64": base64.b64encode(encoded).decode() if ok else None,
    }
