import sqlite3

from settings import DATABASE


def connect():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


def one(sql, params=()):
    with connect() as conn:
        row = conn.execute(sql, params).fetchone()
    return dict(row) if row else None


def all_rows(sql, params=()):
    with connect() as conn:
        return [dict(r) for r in conn.execute(sql, params).fetchall()]


def run(sql, params=()):
    with connect() as conn:
        conn.execute(sql, params)
