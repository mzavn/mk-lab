import hashlib
import hmac
import os
import time

import db
import sessions
from settings import LOGIN_BLOCK_MINUTES, LOGIN_MAX_FAILURES


def hash_password(password, salt=None):
    salt = salt or os.urandom(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, 310_000)
    return salt.hex() + "$" + digest.hex()


def check(password, stored):
    salt_hex = stored.partition("$")[0]
    return hmac.compare_digest(hash_password(password, bytes.fromhex(salt_hex)), stored)


UNKNOWN = hash_password("khong-co-tai-khoan")


def attempt(user, password):
    now = int(time.time())
    slot = db.run(
        "UPDATE users SET failed_logins = failed_logins + 1 WHERE id = ? AND blocked_until <= ? AND failed_logins < ?",
        (user["id"], now, LOGIN_MAX_FAILURES),
    )
    if not slot:
        return False
    if check(password, user["password_hash"]):
        db.run("UPDATE users SET failed_logins = 0 WHERE id = ?", (user["id"],))
        return True
    db.run(
        "UPDATE users SET blocked_until = ?, failed_logins = 0 WHERE id = ? AND failed_logins >= ?",
        (now + LOGIN_BLOCK_MINUTES * 60, user["id"], LOGIN_MAX_FAILURES),
    )
    return False


def set_password(user_id, new_password, keep=None):
    with db.tx() as conn:
        conn.execute("UPDATE users SET password_hash = ? WHERE id = ?", (hash_password(new_password), user_id))
        sessions.revoke_all(conn, user_id, keep=keep)
