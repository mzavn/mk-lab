import time

import db
from web import Denied


def refund(actor, invoice_id, amount):
    if amount <= 0:
        raise ValueError("so tien")
    with db.tx() as conn:
        invoice = conn.execute(
            "SELECT id, amount, status FROM invoices WHERE id = ? AND company_id = ?",
            (invoice_id, actor["company_id"]),
        ).fetchone()
        if invoice is None:
            raise Denied(404, "khong tim thay")
        if invoice["status"] != "paid":
            raise Denied(409, "chi hoan hoa don da thu")
        cur = conn.execute(
            "INSERT INTO refunds (company_id, invoice_id, amount, created_by, at) "
            "SELECT ?, ?, ?, ?, ? WHERE "
            "(SELECT COALESCE(SUM(amount), 0) FROM refunds WHERE invoice_id = ?) + ? <= ?",
            (actor["company_id"], invoice_id, amount, actor["id"], int(time.time()),
             invoice_id, amount, invoice["amount"]),
        )
        if cur.rowcount != 1:
            raise Denied(409, "vuot so tien da thu")
    return {"hoa_don": invoice_id, "hoan": amount}
