import json
from http.server import BaseHTTPRequestHandler
from urllib.parse import parse_qs, urlparse

import assistant
import auth
import confirmations
import invoices
import members
import payhook
import periods
import projects
import public
import reports
import sessions
import web
from settings import MAX_BODY

PUBLIC = {
    ("POST", "/dang-nhap"),
    ("GET", "/chia-se/hoa-don"),
    ("POST", "/thanh-toan/bao"),
}

ROUTES = {
    ("POST", "/dang-nhap"): auth.login,
    ("POST", "/doi-mat-khau"): auth.change_password,
    ("GET", "/toi"): members.profile,
    ("GET", "/thanh-vien"): members.list_members,
    ("POST", "/thanh-vien/khoa"): members.lock_member,
    ("POST", "/thanh-vien/vai"): members.set_role,
    ("GET", "/du-an"): projects.list_projects,
    ("POST", "/du-an"): projects.create_project,
    ("POST", "/du-an/sao-chep"): projects.copy_project,
    ("POST", "/du-an/ngan-sach"): projects.update_budget,
    ("POST", "/du-an/ngan-sach/hang-loat"): projects.bulk_budgets,
    ("POST", "/du-an/luu-tru"): projects.archive_project,
    ("GET", "/hoa-don"): invoices.view_invoice,
    ("POST", "/hoa-don"): invoices.create_draft,
    ("POST", "/hoa-don/sua"): invoices.update_draft,
    ("POST", "/hoa-don/phat-hanh"): invoices.issue,
    ("POST", "/hoa-don/huy"): invoices.void,
    ("POST", "/hoa-don/khoi-phuc"): invoices.restore,
    ("POST", "/hoa-don/ghi-thu"): invoices.record_payment,
    ("POST", "/hoa-don/hoan-tien"): invoices.refund,
    ("POST", "/hoa-don/chia-se"): public.create_link,
    ("GET", "/chia-se/hoa-don"): public.shared_invoice,
    ("POST", "/thanh-toan/bao"): payhook.receive,
    ("POST", "/ky/chot"): periods.close,
    ("GET", "/bao-cao/doanh-thu"): reports.revenue,
    ("GET", "/bao-cao/du-an"): reports.project_lines,
    ("POST", "/tro-ly/xac-nhan"): confirmations.request_code,
    ("POST", "/tro-ly/goi-tool"): assistant.call_tool,
}


class Handler(BaseHTTPRequestHandler):
    def dispatch(self, method):
        url = urlparse(self.path)
        key = (method, url.path)
        route = ROUTES.get(key)
        if route is None:
            return web.send(self, 404, {"loi": "khong tim thay"})
        try:
            length = int(self.headers.get("Content-Length") or 0)
            if not 0 <= length <= MAX_BODY:
                return web.send(self, 413, {"loi": "yeu cau qua lon"})
            raw = self.rfile.read(length) if length else b""
            body = {}
            if raw and (self.headers.get("Content-Type") or "").startswith("application/json"):
                body = json.loads(raw)
            if not isinstance(body, dict):
                raise ValueError("body")
            req = {
                "query": {k: v[0] for k, v in parse_qs(url.query).items()},
                "body": body,
                "raw": raw,
                "headers": self.headers,
                "user": sessions.current_user(self.headers.get("Authorization")),
            }
            if req["user"] is None and key not in PUBLIC:
                return web.send(self, 401, {"loi": "can dang nhap"})
            status, payload = route(req)
        except web.Denied as err:
            return web.send(self, err.status, {"loi": err.message})
        except (ValueError, KeyError, TypeError):
            return web.send(self, 400, {"loi": "du lieu khong hop le"})
        web.send(self, status, payload)

    def do_GET(self):
        self.dispatch("GET")

    def do_POST(self):
        self.dispatch("POST")

    def log_message(self, fmt, *args):
        import sys
        sys.stderr.write("%s %s\n" % (self.command, urlparse(self.path).path))
