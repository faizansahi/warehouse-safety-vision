# Verification status

Local Windows execution on 7 September 2026 passed 7 tests with 87% statement coverage. Ruff lint, formatting, and source compilation passed. Raw reports are in this directory.

The actual YOLO11n model detected **1 person with confidence 0.899** in a NASA public-domain portrait. A deliberately illustrative zone covering that person's foot point generated **1 HIGH PERSON_IN_RESTRICTED_ZONE event**, confirmed through the event API. Boxes come from model output; the orange polygon is configuration. This sample demonstrates the workflow and does not measure warehouse detection quality.

Docker was unavailable on the local Windows machine. Docker Compose and PostgreSQL 16 were verified successfully on a GitHub-hosted Ubuntu runner.

[Successful CI run 34070971634](https://github.com/faizansahi/warehouse-safety-vision/actions/runs/34070971634) passed both the quality and containers jobs. The run includes dependency resolution, lint, formatting, tests, Compose validation, image build, container execution, and PostgreSQL checks.

The Linux container ran actual YOLO inference on the attributed NASA image, returned a person-zone event, and confirmed it through PostgreSQL. A second real annotated frame is saved as [docker-frame.jpg](docker-frame.jpg).

[Downloaded container execution artifact](docker-demo.json) preserves the actual results from that run. These artifacts are separate from the local SQLite demo.

The test output retains upstream Starlette/httpx deprecation warnings; no tests were skipped because of them.
