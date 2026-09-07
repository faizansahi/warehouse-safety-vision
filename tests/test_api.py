import cv2
import numpy as np
from fastapi.testclient import TestClient

from warehouse_vision import main
from warehouse_vision.domain import Detection


def test_api_persists_rule_events_with_stub_detector(monkeypatch):
    class Detector:
        def detect(self, frame):
            return [Detection("person", 0.9, (20, 20, 80, 180))]

    monkeypatch.setattr(main, "get_detector", lambda: Detector())
    ok, encoded = cv2.imencode(".jpg", np.zeros((300, 400, 3), dtype=np.uint8))
    assert ok
    with TestClient(main.app) as api:
        result = api.post(
            "/analyze/frame", files={"file": ("unit-fixture.jpg", encoded.tobytes(), "image/jpeg")}
        )
        assert result.status_code == 200
        assert result.json()["events"][0]["type"] == "PERSON_IN_RESTRICTED_ZONE"
        assert api.get("/events").json()[0]["source"] == "unit-fixture.jpg"
        assert api.get("/events?limit=-1").status_code == 422
        assert (
            api.post("/analyze/frame", files={"file": ("bad.jpg", b"", "image/jpeg")}).status_code
            == 422
        )


def test_model_failure_is_safe_and_persisted(monkeypatch):
    def unavailable():
        raise RuntimeError("private internal error detail")

    monkeypatch.setattr(main, "get_detector", unavailable)
    ok, encoded = cv2.imencode(".jpg", np.zeros((20, 20, 3), dtype=np.uint8))
    assert ok
    with TestClient(main.app) as api:
        result = api.post(
            "/analyze/frame", files={"file": ("fixture.jpg", encoded.tobytes(), "image/jpeg")}
        )
        assert result.status_code == 503
        event = api.get("/events").json()[0]
        assert event["type"] == "SYSTEM_ERROR"
        assert "private" not in str(event)
