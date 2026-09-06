from pathlib import Path

from .domain import Detection


class YoloDetector:
    def __init__(self, weights: str = "yolo11n.pt", confidence: float = 0.4):
        from ultralytics import YOLO

        self.model = YOLO(weights)
        self.confidence = confidence
        self.custom = Path(weights).name not in {"yolo11n.pt", "yolov8n.pt"}

    def detect(self, frame) -> list[Detection]:
        result = self.model.predict(frame, conf=self.confidence, verbose=False)[0]
        detections = []
        for box in result.boxes:
            label = result.names[int(box.cls[0])]
            # COCO has people and road vehicles, but no reliable forklift or PPE class.
            if label == "person" or (
                self.custom and label in {"forklift", "industrial_vehicle", "helmet", "no_helmet"}
            ):
                detections.append(
                    Detection(
                        label, float(box.conf[0]), tuple(int(x) for x in box.xyxy[0].tolist())
                    )
                )
        return detections
