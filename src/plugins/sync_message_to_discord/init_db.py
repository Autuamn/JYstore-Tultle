from pathlib import Path
import sqlite3


async def init_db(dbpath: Path):
    conn = sqlite3.connect(dbpath)
    conn.execute(
        """CREATE TABLE ID (
            DCID    INT     NOT NULL,
            QQID    TEXT    NOT NULL
        );"""
    )
    return conn
