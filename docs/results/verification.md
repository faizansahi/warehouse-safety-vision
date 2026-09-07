# Executed checks

On 7 September 2026, Python 3.12.6 on Windows passed **7 tests** with
**87% statement coverage**. Ruff lint, formatting checks, dependency resolution,
`pip check`, and source compilation passed. The API demos import and run the application;
compilation alone is not a runtime import test.

Ran YOLO11n on the attributed warehouse photograph: one person, confidence 0.758, box [765, 244, 999, 645]. The configured demo polygon triggered one HIGH PERSON_IN_RESTRICTED_ZONE event, retrieved from SQLite. The person-only image comes from a separate actual inference.

[Actual local responses](demo.json) · [Test report](tests.txt) · [Check exit codes](checks.json)

Absolute virtual-environment paths in reports are replaced with `<venv>` for portability.
The test report retains upstream FastAPI/Starlette deprecation warnings.

Docker is unavailable on the local Windows machine. [CI run 34073515227](https://github.com/faizansahi/warehouse-safety-vision/actions/runs/34073515227)
passed quality and container jobs on GitHub-hosted Ubuntu with PostgreSQL 16.
This includes dependency installation, tests, lint, formatting, Compose validation,
image build, and the running container workflow.

The container ran real YOLO inference on the same warehouse photograph, triggered the configured zone event, and queried it from PostgreSQL. The returned annotation is [docker-frame.jpg](docker-frame.jpg).

[Downloaded container results](docker-demo.json) are the actual artifact from that run.
