import base64
import re
import urllib.request

import db
from settings import AVATAR_MAX_BYTES

USER_COLUMNS = ("display_name", "phone", "email", "role", "points")
PHONE = re.compile(r"^0\d{9}$")


def update_profile(req):
    if req["user_id"] is None:
        return 401, {"loi": "can dang nhap"}
    changes = {k: v for k, v in req["body"].items() if k in USER_COLUMNS}
    if "phone" in changes and not PHONE.match(str(changes["phone"])):
        return 400, {"loi": "so dien thoai khong hop le"}
    if not changes:
        return 400, {"loi": "khong co gi de doi"}
    assignments = ", ".join(f"{col} = ?" for col in changes)
    db.run(f"UPDATE users SET {assignments} WHERE id = ?", (*changes.values(), req["user_id"]))
    return 200, {"ok": True}


def set_avatar(req):
    if req["user_id"] is None:
        return 401, {"loi": "can dang nhap"}
    url = str(req["body"].get("url", ""))
    if not url.startswith(("http://", "https://")):
        return 400, {"loi": "duong dan khong hop le"}
    with urllib.request.urlopen(url, timeout=5) as resp:
        data = resp.read(AVATAR_MAX_BYTES)
    db.run("UPDATE users SET avatar = ? WHERE id = ?", (data, req["user_id"]))
    return 200, {"ok": True, "kich_thuoc": len(data)}


def get_avatar(req):
    if req["user_id"] is None:
        return 401, {"loi": "can dang nhap"}
    user = db.one("SELECT avatar FROM users WHERE id = ?", (req["user_id"],))
    data = user["avatar"] if user and user["avatar"] else b""
    return 200, {"anh": base64.b64encode(data).decode("ascii")}
