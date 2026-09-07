# Engineering decisions

## Accepted baseline

Keep model output separate from pure geometry rules so rule tests need no weights. Reuse one detector and serialize calls. Interpret bounding-box maximum coordinates as exclusive when finding a foot point. Store safe error categories rather than internal exception text.

## Testing strategy

Keep deterministic domain tests separate from HTTP/database integration and real model demos. Unit-test stubs are never presented as model evidence. Capture actual responses and preserve the commands needed to reproduce them.

## Tradeoffs

COCO weights do not supply forklift or PPE classes; those rules require validated custom weights. A portrait is not an industrial test dataset. Pixel proximity is perspective-dependent. There is no tracking, event deduplication, calibrated distance, authentication, or safety certification. Repeated video frames may produce repeated events. The detector is exercised by the separate real demo, not by unit-test model mocks.

## Next steps

Use a licensed warehouse dataset, evaluate custom forklift/PPE models, add tracking and event deduplication, and calibrate camera geometry for robotics or industrial inspection experiments.
