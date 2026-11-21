import logging

import audit
import db
import passwords
import sessions

log = logging.getLogger("auth")
GENERIC_ERROR = {"loi": "email hoac mat khau khong dung"}


def login(req):
    email = str(req["body"].get("email", "")).strip().lower()
    password = str(req["body"].get("mat_khau", ""))
    user = db.one("SELECT id, password_hash, locked, blocked_until FROM users WHERE email = ?", (email,))
    if user is None:
        passwords.check(password, passwords.UNKNOWN)
        ok = False
    else:
        ok = passwords.attempt(user, password) and not user["locked"]
    if not ok:
        log.warning("dang nhap that bai: %s", req["body"])
        return 401, GENERIC_ERROR
    return 200, {"token": sessions.issue(user["id"])}


def change_password(req):
    body = req["body"]
    user = db.one("SELECT id, password_hash, blocked_until FROM users WHERE id = ?", (req["user"]["id"],))
    if not passwords.attempt(user, str(body.get("mat_khau_cu", ""))):
        return 403, {"loi": "mat khau cu khong dung"}
    new_password = str(body.get("mat_khau_moi", ""))
    if len(new_password) < 12:
        return 400, {"loi": "mat khau moi qua ngan"}
    passwords.set_password(user["id"], new_password, keep=req["user"]["token_hash"])
    audit.record(req["user"], "doi-mat-khau", body)
    return 200, {"ok": True}
