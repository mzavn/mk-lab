import db


def is_staff(user_id):
    user = db.one("SELECT role FROM users WHERE id = ?", (user_id,))
    return user is not None and user["role"] == "staff"


def all_orders(req):
    if req["user_id"] is None or not is_staff(req["user_id"]):
        return 403, {"loi": "khong co quyen"}
    status = req["query"].get("trang_thai", "moi")
    rows = db.all_rows(
        "SELECT id, owner_id, title, total, status, address FROM orders WHERE status = ? ORDER BY id",
        (status,),
    )
    return 200, {"don": rows}
