import aiosqlite
from datetime import datetime
from typing import List, Dict, Any, Optional
DB_PATH = "resqwear.sqlite"

class DB:
    def __init__(self, path: str = DB_PATH):
        self.path = path

    async def init(self):
        async with aiosqlite.connect(self.path) as db:
            await db.executescript("""
            PRAGMA journal_mode=WAL;

            CREATE TABLE IF NOT EXISTS devices(
              device_id TEXT PRIMARY KEY,
              name TEXT,
              scenario TEXT,
              status TEXT,
              last_seen TEXT
            );

            CREATE TABLE IF NOT EXISTS positions(
              id INTEGER PRIMARY KEY AUTOINCREMENT,
              device_id TEXT,
              ts TEXT,
              lat REAL,
              lon REAL,
              speed_kph REAL,
              transport TEXT
            );

            CREATE TABLE IF NOT EXISTS temps(
              id INTEGER PRIMARY KEY AUTOINCREMENT,
              device_id TEXT,
              ts TEXT,
              temp_c REAL,
              transport TEXT
            );

            CREATE TABLE IF NOT EXISTS alerts(
              alert_id TEXT PRIMARY KEY,
              device_id TEXT,
              alert_type TEXT,
              message TEXT,
              severity INTEGER,
              ts TEXT,
              resolved INTEGER
            );
            """)
            await db.commit()

    async def upsert_device(self, device_id: str, name: str, scenario: str, status: str, last_seen: datetime):
        async with aiosqlite.connect(self.path) as db:
            await db.execute("""
              INSERT INTO devices(device_id,name,scenario,status,last_seen)
              VALUES(?,?,?,?,?)
              ON CONFLICT(device_id) DO UPDATE SET
                name=excluded.name,
                scenario=excluded.scenario,
                status=excluded.status,
                last_seen=excluded.last_seen
            """, (device_id, name, scenario, status, last_seen.isoformat()))
            await db.commit()

    async def insert_position(self, device_id: str, ts: datetime, lat: float, lon: float, speed_kph: float, transport: str):
        async with aiosqlite.connect(self.path) as db:
            await db.execute(
                "INSERT INTO positions(device_id,ts,lat,lon,speed_kph,transport) VALUES(?,?,?,?,?,?)",
                (device_id, ts.isoformat(), lat, lon, speed_kph, transport)
            )
            await db.commit()

    async def insert_temp(self, device_id: str, ts: datetime, temp_c: float, transport: str):
        async with aiosqlite.connect(self.path) as db:
            await db.execute(
                "INSERT INTO temps(device_id,ts,temp_c,transport) VALUES(?,?,?,?)",
                (device_id, ts.isoformat(), temp_c, transport)
            )
            await db.commit()

    async def upsert_alert(self, alert_id: str, device_id: str, alert_type: str, message: str, severity: int, ts: datetime, resolved: bool = False):
        async with aiosqlite.connect(self.path) as db:
            await db.execute("""
              INSERT INTO alerts(alert_id,device_id,alert_type,message,severity,ts,resolved)
              VALUES(?,?,?,?,?,?,?)
              ON CONFLICT(alert_id) DO UPDATE SET
                resolved=excluded.resolved
            """, (alert_id, device_id, alert_type, message, severity, ts.isoformat(), 1 if resolved else 0))
            await db.commit()

    async def resolve_alert(self, alert_id: str):
        async with aiosqlite.connect(self.path) as db:
            await db.execute("UPDATE alerts SET resolved=1 WHERE alert_id=?", (alert_id,))
            await db.commit()

    async def list_devices(self) -> List[Dict[str, Any]]:
        async with aiosqlite.connect(self.path) as db:
            db.row_factory = aiosqlite.Row
            cur = await db.execute("SELECT * FROM devices ORDER BY name")
            return [dict(r) for r in await cur.fetchall()]

    async def active_alerts(self) -> List[Dict[str, Any]]:
        async with aiosqlite.connect(self.path) as db:
            db.row_factory = aiosqlite.Row
            cur = await db.execute("SELECT * FROM alerts WHERE resolved=0 ORDER BY ts DESC")
            return [dict(r) for r in await cur.fetchall()]

    async def last_known(self, device_id: str) -> Optional[Dict[str, Any]]:
        async with aiosqlite.connect(self.path) as db:
            db.row_factory = aiosqlite.Row
            cur = await db.execute(
              "SELECT * FROM positions WHERE device_id=? ORDER BY ts DESC LIMIT 1", (device_id,))
            r = await cur.fetchone()
            return dict(r) if r else None

    async def hourly_positions(self, device_id: str, hours: int = 24) -> List[Dict[str, Any]]:
        async with aiosqlite.connect(self.path) as db:
            db.row_factory = aiosqlite.Row
            cur = await db.execute("""
              SELECT * FROM positions
              WHERE device_id=?
              AND ts >= datetime('now', ? || ' hours')
              ORDER BY ts
            """, (device_id, f"-{hours}"))
            return [dict(r) for r in await cur.fetchall()]

    async def temps_series(self, device_id: str, minutes: int = 120) -> List[Dict[str, Any]]:
        async with aiosqlite.connect(self.path) as db:
            db.row_factory = aiosqlite.Row
            cur = await db.execute("""
              SELECT * FROM temps
              WHERE device_id=?
              AND ts >= datetime('now', ? || ' minutes')
              ORDER BY ts
            """, (device_id, f"-{minutes}"))
            return [dict(r) for r in await cur.fetchall()]
