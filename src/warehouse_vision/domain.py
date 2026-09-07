from dataclasses import dataclass
from enum import StrEnum

import cv2
import numpy as np


class EventType(StrEnum):
    PERSON_IN_RESTRICTED_ZONE = "PERSON_IN_RESTRICTED_ZONE"
    FORKLIFT_IN_PEDESTRIAN_ZONE = "FORKLIFT_IN_PEDESTRIAN_ZONE"
    PERSON_FORKLIFT_PROXIMITY = "PERSON_FORKLIFT_PROXIMITY"
    PPE_VIOLATION = "PPE_VIOLATION"
    SYSTEM_ERROR = "SYSTEM_ERROR"


class Severity(StrEnum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"


class ZoneKind(StrEnum):
    RESTRICTED = "restricted"
    PEDESTRIAN_ONLY = "pedestrian_only"


@dataclass(frozen=True)
class Detection:
    label: str
    confidence: float
    box: tuple[int, int, int, int]

    @property
    def foot(self) -> tuple[int, int]:
        return ((self.box[0] + self.box[2]) // 2, max(self.box[1], self.box[3] - 1))

    @property
    def center(self) -> tuple[int, int]:
        return ((self.box[0] + self.box[2]) // 2, (self.box[1] + self.box[3]) // 2)


@dataclass(frozen=True)
class Zone:
    name: str
    kind: ZoneKind
    polygon: list[tuple[int, int]]


def contains(zone: Zone, point: tuple[int, int]) -> bool:
    return cv2.pointPolygonTest(np.array(zone.polygon, np.int32), point, False) >= 0


def distance(a: Detection, b: Detection) -> float:
    return float(np.linalg.norm(np.array(a.center) - np.array(b.center)))


def evaluate(
    detections: list[Detection], zones: list[Zone], proximity_px: float = 120
) -> list[dict]:
    events = []
    people = [d for d in detections if d.label == "person"]
    vehicles = [d for d in detections if d.label in {"forklift", "industrial_vehicle"}]
    for detection in detections:
        if detection.label == "no_helmet":
            events.append({"type": EventType.PPE_VIOLATION, "severity": Severity.HIGH})
    for person in people:
        for zone in zones:
            if zone.kind == ZoneKind.RESTRICTED and contains(zone, person.foot):
                events.append(
                    {
                        "type": EventType.PERSON_IN_RESTRICTED_ZONE,
                        "severity": Severity.HIGH,
                        "zone": zone.name,
                    }
                )
    for vehicle in vehicles:
        for zone in zones:
            if zone.kind == ZoneKind.PEDESTRIAN_ONLY and contains(zone, vehicle.foot):
                events.append(
                    {
                        "type": EventType.FORKLIFT_IN_PEDESTRIAN_ZONE,
                        "severity": Severity.HIGH,
                        "zone": zone.name,
                    }
                )
    for person in people:
        for vehicle in vehicles:
            gap = distance(person, vehicle)
            if gap < proximity_px:
                events.append(
                    {
                        "type": EventType.PERSON_FORKLIFT_PROXIMITY,
                        "severity": Severity.HIGH if gap < proximity_px / 2 else Severity.MEDIUM,
                        "distance_px": round(gap, 1),
                    }
                )
    return events
