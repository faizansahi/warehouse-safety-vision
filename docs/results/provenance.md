# Evidence provenance
The sample is the public-domain NASA astronaut portrait described in [third-party notices](../../THIRD_PARTY_NOTICES.md). Input bytes and SHA-256 are recorded with actual results in `demo.json`.

`../images/demo.jpg` is the JPEG returned by the live FastAPI endpoint after actual YOLO11n inference. Green person boxes and confidence are model output; the orange polygon comes from `config/zones.demo.json`. The zone is deliberately illustrative and covers the detected person's foot point. The event was evaluated by the application's rule engine and read back from its SQLite event database.

`../images/swagger.png` is a real browser screenshot. This demonstration is not a warehouse accuracy study. Unit tests use explicitly mocked detections and do not produce this image.

Reproduce with `ZONES_FILE=config/zones.demo.json` set before API startup, then `python scripts/demo_frame.py`.
