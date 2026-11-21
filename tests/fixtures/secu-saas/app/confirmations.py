import json
import secrets
import time

import db
import passwords
import sessions
from settings import CONFIRM_SECONDS
from web import Denied

ACTIONS = ("doi-vai", "hoan-tien")


def subject_of(content):
    return json.dumps(content, sort_keys=True, ensure_ascii=False)


def request_code(req):
    user = db.one(
        "SELECT id, password_hash, blocked_until FROM users WHERE id = ?", (req["user"]["id"],)
    )
    if not passwords.attempt(user, str(req["body"].get("mat_khau", ""))):
        raise Denied(403, "mat khau khong dung")
    action = str(req["body"].get("viec", ""))
    content = req["body"].get("noi_dung")
    if action not in ACTIONS or not isinstance(content, dict):
        raise ValueError("xac nhan")
    code = secrets.token_urlsafe(16)
    db.run(
        "INSERT INTO confirmations (code_hash, user_id, action, subject, expires_at, used) "
        "VALUES (?, ?, ?, ?, ?, 0)",
        (sessions.digest(code), user["id"], action, subject_of(content), int(time.time()) + CONFIRM_SECONDS),
    )
    return 201, {"ma_xac_nhan": code}


def consume(actor, action, code, content):
    changed = db.run(
        "UPDATE confirmations SET used = 1 WHERE code_hash = ? AND user_id = ? AND action = ? "
        "AND subject = ? AND used = 0 AND expires_at > ?",
        (sessions.digest(code), actor["id"], action, subject_of(content), int(time.time())),
    )
    if changed != 1:
        raise Denied(403, "can xac nhan tren man hinh")
