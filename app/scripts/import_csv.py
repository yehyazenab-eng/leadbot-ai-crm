from __future__ import annotations

import csv
import sys
from datetime import datetime
from typing import Optional

from sqlalchemy.orm import Session

from app.crud.leads import create_lead
from app.db.base import init_db
from app.db.session import SessionLocal


def _parse_dt(s: str) -> Optional[datetime]:
    s = (s or "").strip()
    if not s:
        return None
    # Example in existing file: "2026-05-05 17:03:02.172383"
    try:
        return datetime.fromisoformat(s)
    except Exception:
        return None


def run(path: str) -> int:
    init_db()
    db: Session = SessionLocal()
    try:
        with open(path, newline="") as f:
            reader = csv.DictReader(f)
            for row in reader:
                name = (row.get("name") or "").strip()
                phone = (row.get("phone") or "").strip()
                request = (row.get("request") or "").strip()
                lead = create_lead(db, name=name, phone=phone, email="", request=request, source="csv")
                # Keep simple; created_at from DB. For full fidelity we'd use explicit insert.
                _ = _parse_dt(row.get("time") or "")
                print(f"Imported lead #{lead.id}: {lead.name} {lead.phone}")
        return 0
    finally:
        db.close()


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 -m app.scripts.import_csv leads.csv")
        raise SystemExit(2)
    raise SystemExit(run(sys.argv[1]))

