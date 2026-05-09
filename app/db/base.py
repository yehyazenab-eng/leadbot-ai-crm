from app.db.session import engine
from app.models.base import Base
from app.models.lead import Lead, LeadInteraction, LeadNote  # noqa: F401
from app.models.notification import Notification  # noqa: F401


def _ensure_sqlite_column(table: str, column: str, ddl: str) -> None:
    """
    Minimal SQLite migration helper.
    Safe to run on every startup; no-ops if column already exists.
    """
    if not str(engine.url).startswith("sqlite"):
        return

    with engine.begin() as conn:
        rows = conn.exec_driver_sql(f"PRAGMA table_info({table})").fetchall()
        existing = {r[1] for r in rows}  # (cid, name, type, notnull, dflt_value, pk)
        if column in existing:
            return
        conn.exec_driver_sql(f"ALTER TABLE {table} ADD COLUMN {ddl}")


def init_db() -> None:
    Base.metadata.create_all(bind=engine)
    # lightweight migrations for existing sqlite db files
    _ensure_sqlite_column("leads", "summary", "summary TEXT NOT NULL DEFAULT ''")
    _ensure_sqlite_column("leads", "score", "score TEXT NOT NULL DEFAULT 'Low'")

