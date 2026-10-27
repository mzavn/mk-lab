import hashlib
import hmac
import os
import time

import db
from settings import SESSION_DAYS, SIGNING_KEY

GENERIC_ERROR = {"loi": "email hoac mat khau khong dung"}


def hash_password(password, salt=None):
    salt = salt or os.urandom(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, 310_000)
    return salt.hex() + "$" + digest.hex()


def check_password(password, stored):
    salt_hex = stored.partition("$")[0]
    return hmac.compare_digest(hash_password(password, bytes.fromhex(salt_hex)), stored)


UNKNOWN_USER_HASH = hash_password("unknown-user")


def sign(value):
    return hmac.new(SIGNING_KEY.encode(), value.encode(), hashlib.sha256).hexdigest()


def session_cookie(user_id):
    value = f"{user_id}:{int(time.time()) + SESSION_DAYS * 86400}"
    return f"phien={value}.{sign(value)}; Path=/; HttpOnly; Secure; SameSite=Strict"


def read_session(cookie_header):
    for part in (cookie_header or "").split(";"):
        name, _, token = part.strip().partition("=")
        if name != "phien" or "." not in token:
            continue
        value, _, sig = token.rpartition(".")
        user_id, _, expires = value.partition(":")
        if not hmac.compare_digest(sig, sign(value)):
            return None
        if not (user_id.isdigit() and expires.isdigit()) or int(expires) < time.time():
            return None
        return int(user_id)
    return None


def login(req):
    email = str(req["body"].get("email", "")).strip().lower()
    password = str(req["body"].get("mat_khau", ""))
    user = db.one("SELECT id, password_hash FROM users WHERE email = ?", (email,))
    stored = user["password_hash"] if user else UNKNOWN_USER_HASH
    if not check_password(password, stored) or user is None:
        return 401, GENERIC_ERROR
    return 200, {"ok": True}, [("Set-Cookie", session_cookie(user["id"]))]
