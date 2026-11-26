import aiosqlite
import logging
from datetime import datetime, timezone
from config import DB_PATH

logger = logging.getLogger(__name__)


async def init_db() -> None:
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id        INTEGER PRIMARY KEY,
                username       TEXT,
                first_name     TEXT,
                started_at     TEXT NOT NULL,
                consented_at   TEXT,
                invite_sent_at TEXT
            )
        """)
        await db.execute("""
            CREATE TABLE IF NOT EXISTS logs (
                id         INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id    INTEGER,
                action     TEXT NOT NULL,
                details    TEXT,
                created_at TEXT NOT NULL
            )
        """)
        await db.commit()
    logger.info("دیتابیس با موفقیت مقداردهی اولیه شد.")


async def add_or_update_start(
    user_id: int,
    username: str | None,
    first_name: str | None,
) -> None:
    now = datetime.now(timezone.utc).isoformat()
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            INSERT INTO users (user_id, username, first_name, started_at)
            VALUES (?, ?, ?, ?)
            ON CONFLICT(user_id) DO UPDATE SET
                username   = excluded.username,
                first_name = excluded.first_name
        """, (user_id, username, first_name, now))
        await db.commit()


async def mark_consent(user_id: int) -> None:
    now = datetime.now(timezone.utc).isoformat()
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            UPDATE users
            SET consented_at = ?
            WHERE user_id = ?
        """, (now, user_id))
        await db.commit()


async def mark_invite_sent(user_id: int) -> None:
    now = datetime.now(timezone.utc).isoformat()
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            UPDATE users
            SET invite_sent_at = ?
            WHERE user_id = ?
        """, (now, user_id))
        await db.commit()


async def has_consented(user_id: int) -> bool:
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute(
            "SELECT consented_at FROM users WHERE user_id = ?",
            (user_id,)
        ) as cursor:
            row = await cursor.fetchone()
            return bool(row and row[0])


async def log_action(user_id: int | None, action: str, details: str = "") -> None:
    now = datetime.now(timezone.utc).isoformat()
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            INSERT INTO logs (user_id, action, details, created_at)
            VALUES (?, ?, ?, ?)
        """, (user_id, action, details, now))
        await db.commit()
