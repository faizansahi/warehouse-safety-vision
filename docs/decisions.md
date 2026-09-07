# Geometry, inference, and events

The detector converts model output to typed boxes. Default weights supply person detections. Forklift and PPE policies require custom weights with explicit supported labels; other COCO objects are not relabeled.

Zone polygons use image pixels. Point-in-polygon checks include boundaries. The box-bottom midpoint is a foot proxy, with the maximum coordinate treated as exclusive. Cropped or occluded bodies can make this a poor estimate.

Proximity is Euclidean center-to-center pixel distance, not metres. Camera perspective, zoom, and resolution change its meaning. The demo polygon is illustrative and does not assess the photographed worker.

The API caches and serializes model access and runs inference in a threadpool. Model loading is lazy, so process health does not imply inference readiness. Rule events are persisted before annotation is returned. Failures store a safe system-error message; repeated frames can create repeated events.

Geometry tests use typed fixtures and API tests stub inference. The photo demo and container check separately run YOLO. One image proves integration, not detection accuracy.
