import db
import web


def order_page(req):
    order_id = int(req["query"].get("ma", "0"))
    order = db.one("SELECT id, title, total, status FROM orders WHERE id = ?", (order_id,))
    if order is None:
        return 404, {"loi": "khong tim thay"}
    view = web.escaped(order)
    return 200, (
        "<!doctype html><meta charset='utf-8'><title>Don hang</title>"
        f"<h1>{view['title']}</h1>"
        f"<p>Tong: {view['total']} d</p>"
        f"<p>Trang thai: {view['status']}</p>"
    )
