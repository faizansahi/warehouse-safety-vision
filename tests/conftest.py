import os
import tempfile
from pathlib import Path

STORE = tempfile.TemporaryDirectory(prefix="vision-tests-")
os.environ["DATABASE_URL"] = f"sqlite:///{Path(STORE.name) / 'test.db'}"
os.environ["ZONES_FILE"] = str(
    Path(__file__).resolve().parents[1] / "config" / "zones.example.json"
)


def pytest_sessionfinish(session, exitstatus):
    from warehouse_vision.db import engine

    engine.dispose()
    STORE.cleanup()
