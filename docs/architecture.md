# Architecture

```mermaid
flowchart LR
  Image[Image / sampled video frame] --> API[FastAPI upload]
  API --> YOLO[YOLO detector]
  YOLO --> D[Typed detections]
  Zones[JSON polygon configuration] --> Rules[Zone / proximity / PPE rules]
  D --> Rules
  Rules --> DB[(SQLite or PostgreSQL events)]
  D --> Draw[OpenCV annotation]
  Zones --> Draw
  DB --> Events[GET /events]
```

Typed detections feed independent geometry rules and OpenCV annotation. Rules create SQL events. Video processing is a client that submits sampled frames.

See [design decisions](decisions.md) for tradeoffs.
