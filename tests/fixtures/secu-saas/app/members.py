import audit
import db
import roles
import views
from web import Denied


def list_members(req):
    rows = db.all_rows("SELECT * FROM users WHERE company_id = ? ORDER BY name", (req["user"]["company_id"],))
    return 200, {"thanh_vien": rows}


def profile(req):
    row = db.one("SELECT * FROM users WHERE id = ?", (req["user"]["id"],))
    return 200, views.member(row)


def lock_member(req):
    user = req["user"]
    roles.require(user, roles.OWNER)
    member_id = int(req["body"]["ma"])
    changed = db.run(
        "UPDATE users SET locked = 1 WHERE id = ? AND company_id = ? AND role != 'owner'",
        (member_id, user["company_id"]),
    )
    if not changed:
        raise Denied(404, "khong tim thay")
    audit.record(user, "khoa-thanh-vien", {"ma": member_id})
    return 200, {"ok": True}


def apply_role(actor, member_id, role):
    if role not in roles.ASSIGNABLE:
        raise ValueError("vai")
    changed = db.run(
        "UPDATE users SET role = ? WHERE id = ? AND company_id = ? AND role != 'owner'",
        (role, member_id, actor["company_id"]),
    )
    if not changed:
        raise Denied(404, "khong tim thay")
    audit.record(actor, "doi-vai", {"ma": member_id, "vai": role})
    return {"ma": member_id, "vai": role}


def set_role(req):
    roles.require(req["user"], roles.OWNER)
    return 200, apply_role(req["user"], int(req["body"]["ma"]), str(req["body"]["vai"]))
