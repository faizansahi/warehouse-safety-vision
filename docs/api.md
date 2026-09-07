# API
Use `/docs` for Swagger and `/openapi.json` for the schema.

| Method | Route | Behavior |
|---|---|---|
| GET | /health | Process liveness; does not load the model |
| POST | /analyze/frame | Multipart image, actual detections, rule events, annotated JPEG |
| GET | /events | Newest persisted events; limit 1–500 |

The result contains detection count, detection_details (label/confidence/box), events, annotated_jpeg_bytes, and annotated_jpeg_base64. Bounding boxes are model output; drawn polygons come from configuration.

Uploads are limited to 10 MB and decoded images to 25 megapixels. Empty/invalid images return 422; oversized images return 413. Unavailable inference returns 503 and creates a SYSTEM_ERROR event without internal exception text.

Custom weights must expose explicit forklift, industrial_vehicle, helmet, or no_helmet labels to support corresponding industrial rules. Repeated frames are not deduplicated.

[Real model and event API result](results/demo.json). Unit-test detector stubs are separate from this demonstration.
