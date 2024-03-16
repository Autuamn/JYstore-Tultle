import sqlite3


async def init_db(dbpath: str):
    createdb = open(dbpath, "w")
    createdb.close()
    conn = sqlite3.connect(dbpath)
    c = conn.cursor()
    c.execute(
        """CREATE TABLE ID (
            DCID        INT     PRIMARY KEY     NOT NULL,
            QQID        TEXT                    NOT NULL
        );"""
    )
    return conn
