import os
import subprocess
import sys

from sqlalchemy import create_engine, inspect


def test_migrations_use_environment_and_round_trip(tmp_path):
    url = f"sqlite:///{tmp_path / 'migration.db'}"
    env = dict(os.environ, DATABASE_URL=url)
    for target in ["head", "base", "head"]:
        direction = "downgrade" if target == "base" else "upgrade"
        result = subprocess.run(
            [sys.executable, "-m", "alembic", direction, target],
            env=env,
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0, result.stderr
    engine = create_engine(url)
    assert "ix_safety_events_event_type" in {
        entry["name"] for entry in inspect(engine).get_indexes("safety_events")
    }
    engine.dispose()
