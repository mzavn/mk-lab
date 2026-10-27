import json
from http.server import BaseHTTPRequestHandler
from urllib.parse import parse_qs, urlparse

import account
import auth
import db
import orders
import pages
import staff
import web


def owner_only(handler):
    def wrapped(req):
        if req["user_id"] is None:
            return 401, {"loi": "can dang nhap"}
        order_id = int(req["query"].get("ma", "0"))
        order = db.one("SELECT owner_id FROM orders WHERE id = ?", (order_id,))
        if order is None or order["owner_id"] != req["user_id"]:
            return 404, {"loi": "khong tim thay"}
        return handler(req)
    return wrapped


ROUTES = {
    ("POST", "/dang-nhap"): auth.login,
    ("GET", "/don"): orders.list_orders,
    ("GET", "/don/xem"): orders.view_order,
    ("GET", "/don/lich-su"): orders.order_history,
    ("GET", "/don/trang"): owner_only(pages.order_page),
    ("POST", "/ho-so"): account.update_profile,
    ("POST", "/ho-so/anh"): account.set_avatar,
    ("GET", "/ho-so/anh"): account.get_avatar,
    ("GET", "/cua-hang/don"): staff.all_orders,
}


class Handler(BaseHTTPRequestHandler):
    def dispatch(self, method):
        url = urlparse(self.path)
        route = ROUTES.get((method, url.path))
        if route is None:
            return web.send(self, 404, {"loi": "khong tim thay"})
        try:
            body = {}
            if method == "POST":
                length = int(self.headers.get("Content-Length") or 0)
                body = json.loads(self.rfile.read(min(length, 65536)) or b"{}")
            if not isinstance(body, dict):
                raise ValueError("body")
            req = {
                "query": {k: v[0] for k, v in parse_qs(url.query).items()},
                "body": body,
                "user_id": auth.read_session(self.headers.get("Cookie")),
            }
            status, payload, *extra = route(req)
        except ValueError:
            return web.send(self, 400, {"loi": "du lieu khong hop le"})
        web.send(self, status, payload, extra[0] if extra else ())

    def do_GET(self):
        self.dispatch("GET")

    def do_POST(self):
        self.dispatch("POST")
