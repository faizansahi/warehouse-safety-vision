# Demo provenance

The input is the public-domain DVIDS warehouse photograph attributed in [third-party notices](../../THIRD_PARTY_NOTICES.md). Its SHA-256 is stored in `demo.json`.

`../images/safety-zone-alert.jpg` is the actual JPEG returned by FastAPI after YOLO11n inference. Boxes come from the model; the orange polygon comes from `config/zones.demo.json`. The zone is illustrative, not a finding about the worker.

`../images/person-detection.jpg` is saved by Ultralytics from another inference on the same input. `events.html` renders the actual GET /events response, captured in `../images/event-api.png`. `../images/swagger-api.png` captures the running API docs.

Set `ZONES_FILE=config/zones.demo.json` before API startup and run `python scripts/demo_frame.py`. Local evidence uses SQLite; container evidence uses PostgreSQL. A single photo is not a benchmark.
