import cv2
import numpy as np

from warehouse_vision.domain import Detection, EventType, Severity, Zone, ZoneKind, evaluate


def test_restricted_zone_and_proximity_rules():
    zone = Zone("dock", ZoneKind.RESTRICTED, [(0, 0), (200, 0), (200, 200), (0, 200)])
    events = evaluate(
        [
            Detection("person", 0.9, (40, 40, 80, 120)),
            Detection("forklift", 0.9, (70, 60, 130, 140)),
        ],
        [zone],
        100,
    )
    assert {e["type"] for e in events} == {
        EventType.PERSON_IN_RESTRICTED_ZONE,
        EventType.PERSON_FORKLIFT_PROXIMITY,
    }
    assert any(e["severity"] in {Severity.MEDIUM, Severity.HIGH} for e in events)


def test_vehicle_in_pedestrian_zone_and_outside_is_safe():
    zone = Zone("walkway", ZoneKind.PEDESTRIAN_ONLY, [(0, 0), (100, 0), (100, 100), (0, 100)])
    assert (
        evaluate([Detection("forklift", 0.8, (10, 10, 50, 50))], [zone])[0]["type"]
        == EventType.FORKLIFT_IN_PEDESTRIAN_ZONE
    )
    assert evaluate([Detection("person", 0.8, (300, 300, 350, 400))], [zone]) == []


def test_generated_frame_fixture_is_valid():
    image = np.zeros((240, 320, 3), dtype=np.uint8)
    cv2.rectangle(image, (20, 20), (80, 180), (255, 255, 255), -1)
    ok, data = cv2.imencode(".jpg", image)
    assert ok and cv2.imdecode(data, cv2.IMREAD_COLOR).shape == (240, 320, 3)


def test_ppe_requires_explicit_no_helmet_class():
    events = evaluate([Detection("no_helmet", 0.91, (10, 10, 40, 60))], [])
    assert events == [{"type": EventType.PPE_VIOLATION, "severity": Severity.HIGH}]
    assert evaluate([Detection("person", 0.91, (10, 10, 40, 60))], []) == []
