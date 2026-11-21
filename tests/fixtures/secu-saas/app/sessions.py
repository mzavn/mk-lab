import hashlib
import secrets
import time

import db
from settings import SESSION_HOURS


def digest(token):
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


def issue(user_id):
    token = secrets.token_urlsafe(32)
    db.run(
        "INSERT INTO sessions (token_hash, user_id, expires_at) VALUES (?, ?, ?)",
        (digest(token), user_id, int(time.time()) + SESSION_HOURS * 3600),
    )
    return token


def current_user(authorization):
    scheme, _, token = (authorization or "").partition(" ")
    if scheme != "Bearer" or not token:
        return None
    return db.one(
        "SELECT u.id, u.company_id, u.role, u.name, s.token_hash FROM sessions s "
        "JOIN users u ON u.id = s.user_id WHERE s.token_hash = ? AND s.expires_at > ?",
        (digest(token), int(time.time())),
    )


def revoke_all(conn, user_id, keep=None):
    conn.execute("DELETE FROM sessions WHERE user_id = ? AND token_hash IS NOT ?", (user_id, keep))
