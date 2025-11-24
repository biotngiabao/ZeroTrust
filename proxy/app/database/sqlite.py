# db.py
import aiosqlite
import os
from pathlib import Path


DB_PATH = os.getenv("LAST_SEEN_DB", "data/last_seen.db")

async def init_db(app):
    Path(DB_PATH).parent.mkdir(parents=True, exist_ok=True)
    app.state.db = await aiosqlite.connect(DB_PATH)
    await app.state.db.execute("PRAGMA journal_mode=WAL;")
    await app.state.db.execute("PRAGMA synchronous=NORMAL;")
    await app.state.db.execute(
        """
        CREATE TABLE IF NOT EXISTS last_seen (
            email TEXT PRIMARY KEY,
            ip TEXT,
            device TEXT,
            country TEXT,
            city TEXT,
            updated_at INTEGER
        )
        """
    )
    await app.state.db.commit()

async def close_db(app):
    await app.state.db.close()

async def get_last_seen(db, email: str):
    cur = await db.execute(
        "SELECT ip, device, country, city, updated_at FROM last_seen WHERE email = ?",
        (email,),
    )
    row = await cur.fetchone()
    await cur.close()
    if not row:
        return None
    ip, device, country, city, updated_at = row
    return {"ip": ip, "device": device, "country": country, "city": city, "updated_at": updated_at}

async def upsert_last_seen(db, email: str, ip: str, device: str, country: str, city: str, ts: int):
    await db.execute(
        """
        INSERT INTO last_seen (email, ip, device, country, city, updated_at)
        VALUES (?, ?, ?, ?, ?, ?)
        ON CONFLICT(email) DO UPDATE SET
            ip=excluded.ip,
            device=excluded.device,
            country=excluded.country,
            city=excluded.city,
            updated_at=excluded.updated_at
        """,
        (email, ip, device, country, city, ts),
    )
    await db.commit()
