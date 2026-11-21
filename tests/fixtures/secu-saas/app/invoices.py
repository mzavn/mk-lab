import time

import billing
import db
import periods
import projects
import roles
import views
from web import Denied

MAX_LINES = 100


def load(company_id, invoice_id):
    row = db.one("SELECT * FROM invoices WHERE id = ? AND company_id = ?", (invoice_id, company_id))
    if row is None:
        raise Denied(404, "khong tim thay")
    return row


def _lines(raw):
    if not isinstance(raw, list) or not 0 < len(raw) <= MAX_LINES:
        raise ValueError("dong")
    lines = []
    for item in raw:
        quantity, unit_price = int(item["so_luong"]), int(item["don_gia"])
        if quantity <= 0 or unit_price < 0:
            raise ValueError("dong")
        lines.append((str(item["mo_ta"])[:200], quantity, unit_price))
    return lines


def _write_lines(conn, invoice_id, lines):
    conn.execute("DELETE FROM invoice_lines WHERE invoice_id = ?", (invoice_id,))
    conn.executemany(
        "INSERT INTO invoice_lines (invoice_id, description, quantity, unit_price) VALUES (?, ?, ?, ?)",
        [(invoice_id, *line) for line in lines],
    )
    conn.execute("UPDATE invoices SET amount = ? WHERE id = ?", (sum(q * p for _, q, p in lines), invoice_id))


def view_invoice(req):
    return 200, views.invoice(load(req["user"]["company_id"], int(req["query"].get("ma", 0))))


def create_draft(req):
    user, body = req["user"], req["body"]
    roles.require(user, roles.DRAFTERS)
    project = projects.load_in_company(user["company_id"], int(body["du_an"]))
    period = periods.parse(body["ky"])
    periods.ensure_open(user["company_id"], period)
    lines = _lines(body.get("dong"))
    with db.tx() as conn:
        cur = conn.execute(
            "INSERT INTO invoices (company_id, project_id, customer_name, amount, status, period) "
            "VALUES (?, ?, ?, 0, 'draft', ?)",
            (user["company_id"], project["id"], str(body["khach"])[:200], period),
        )
        _write_lines(conn, cur.lastrowid, lines)
    return 201, {"ma": cur.lastrowid}


def update_draft(req):
    user, body = req["user"], req["body"]
    roles.require(user, roles.DRAFTERS)
    invoice = load(user["company_id"], int(body["ma"]))
    periods.ensure_open(user["company_id"], invoice["period"])
    lines = _lines(body.get("dong"))
    with db.tx() as conn:
        cur = conn.execute(
            "UPDATE invoices SET customer_name = ? WHERE id = ? AND status = 'draft'",
            (str(body["khach"])[:200], invoice["id"]),
        )
        if cur.rowcount != 1:
            raise Denied(409, "chi sua hoa don nhap")
        _write_lines(conn, invoice["id"], lines)
    return 200, {"ok": True}


def issue(req):
    user = req["user"]
    roles.require(user, roles.FINANCE)
    invoice = load(user["company_id"], int(req["body"]["ma"]))
    periods.ensure_open(user["company_id"], invoice["period"])
    changed = db.run(
        "UPDATE invoices SET status = 'issued', issued_at = ? WHERE id = ? AND status = 'draft'",
        (int(time.time()), invoice["id"]),
    )
    if not changed:
        raise Denied(409, "chi phat hanh hoa don nhap")
    return 200, {"ok": True}


def void(req):
    user = req["user"]
    roles.require(user, roles.FINANCE)
    invoice = load(user["company_id"], int(req["body"]["ma"]))
    periods.ensure_open(user["company_id"], invoice["period"])
    changed = db.run(
        "UPDATE invoices SET status = 'void' WHERE id = ? AND status IN ('draft', 'issued')",
        (invoice["id"],),
    )
    if not changed:
        raise Denied(409, "khong huy duoc hoa don nay")
    return 200, {"ok": True}


def restore(req):
    user = req["user"]
    roles.require(user, roles.FINANCE)
    invoice = load(user["company_id"], int(req["body"]["ma"]))
    status = "issued" if invoice["issued_at"] else "draft"
    changed = db.run("UPDATE invoices SET status = ? WHERE id = ? AND status = 'void'", (status, invoice["id"]))
    if not changed:
        raise Denied(409, "hoa don khong o trang thai huy")
    return 200, {"ok": True, "trang_thai": status}


def record_payment(req):
    user = req["user"]
    roles.require(user, roles.FINANCE)
    invoice = load(user["company_id"], int(req["body"]["ma"]))
    with db.tx() as conn:
        cur = conn.execute("UPDATE invoices SET status = 'paid' WHERE id = ? AND status = 'issued'", (invoice["id"],))
        if cur.rowcount != 1:
            raise Denied(409, "chi ghi thu hoa don da phat hanh")
        conn.execute(
            "INSERT INTO payments (invoice_id, amount, at) VALUES (?, ?, ?)",
            (invoice["id"], invoice["amount"], int(time.time())),
        )
    return 200, {"ok": True}


def refund(req):
    roles.require(req["user"], roles.FINANCE)
    return 200, billing.refund(req["user"], int(req["body"]["ma"]), int(req["body"]["so_tien"]))
