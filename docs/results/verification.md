# Verification status

Local Windows execution on 7 September 2026 passed 7 tests with 87% statement coverage. Ruff lint, formatting, and source compilation passed. Raw reports are in this directory.

The actual YOLO11n model detected **1 person with confidence 0.899** in a NASA public-domain portrait. A deliberately illustrative zone covering that person's foot point generated **1 HIGH PERSON_IN_RESTRICTED_ZONE event**, confirmed through the event API. Boxes come from model output; the orange polygon is configuration. This sample demonstrates the workflow and does not measure warehouse detection quality.

Docker and PostgreSQL execution were unavailable locally. GitHub Actions container verification is pending publication; this record will be updated after an actual run.

The test output retains upstream Starlette/httpx deprecation warnings; no tests were skipped because of them.
