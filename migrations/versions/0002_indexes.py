"""Align migration indexes with ORM lookup fields."""

from alembic import op

revision = "0002"
down_revision = "0001"
branch_labels = None
depends_on = None


def upgrade():
    op.create_index("ix_safety_events_event_type", "safety_events", ["event_type"])
    op.create_index("ix_safety_events_severity", "safety_events", ["severity"])


def downgrade():
    op.drop_index("ix_safety_events_severity", table_name="safety_events")
    op.drop_index("ix_safety_events_event_type", table_name="safety_events")
