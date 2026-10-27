import db
import queries


def list_orders(req):
    if req["user_id"] is None:
        return 401, {"loi": "can dang nhap"}
    keyword = req["query"].get("tim", "")
    sql = (
        "SELECT id, title, total, status FROM orders "
        f"WHERE owner_id = ? AND title LIKE '%{keyword}%' ORDER BY id DESC"
    )
    return 200, {"don": db.all_rows(sql, (req["user_id"],))}


def view_order(req):
    if req["user_id"] is None:
        return 401, {"loi": "can dang nhap"}
    order_id = int(req["query"].get("ma", "0"))
    order = db.one(
        "SELECT id, owner_id, title, total, status, address FROM orders WHERE id = ?",
        (order_id,),
    )
    if order is None:
        return 404, {"loi": "khong tim thay"}
    return 200, order


def order_history(req):
    if req["user_id"] is None:
        return 401, {"loi": "can dang nhap"}
    page = max(1, int(req["query"].get("trang", "1")))
    return 200, {"don": db.all_rows(queries.recent_orders_sql(page), (req["user_id"],))}
