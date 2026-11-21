import secrets
import time

import db
import invoices
import paging
import roles
import sessions
import views
from settings import SHARE_LINK_DAYS
from web import Denied


def create_link(req):
    user = req["user"]
    roles.require(user, roles.FINANCE)
    invoice = invoices.load(user["company_id"], int(req["body"]["ma"]))
    if invoice["status"] not in ("issued", "paid"):
        raise Denied(409, "chi chia se hoa don da phat hanh")
    key = secrets.token_urlsafe(24)
    db.run(
        "INSERT INTO share_links (key_hash, invoice_id, expires_at) VALUES (?, ?, ?)",
        (sessions.digest(key), invoice["id"], int(time.time()) + SHARE_LINK_DAYS * 86400),
    )
    return 201, {"khoa": key}


def shared_invoice(req):
    link = db.one(
        "SELECT invoice_id FROM share_links WHERE key_hash = ? AND expires_at > ?",
        (sessions.digest(str(req["query"].get("khoa", ""))), int(time.time())),
    )
    if link is None:
        raise Denied(404, "khong tim thay")
    invoice = db.one("SELECT * FROM invoices WHERE id = ? AND status IN ('issued', 'paid')", (link["invoice_id"],))
    if invoice is None:
        raise Denied(404, "khong tim thay")
    limit, offset = paging.window(req["query"])
    lines = db.all_rows(
        "SELECT description, quantity, unit_price FROM invoice_lines WHERE invoice_id = ? "
        "ORDER BY id LIMIT ? OFFSET ?",
        (invoice["id"], limit, offset),
    )
    return 200, {"hoa_don": views.public_invoice(invoice), "dong": lines}
