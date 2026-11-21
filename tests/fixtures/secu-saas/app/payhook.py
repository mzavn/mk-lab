import hashlib
import hmac
import json
import os
import time
import zlib

import db
from web import Denied


def _signature(raw):
    return hmac.new(os.environ["PAYHOOK_KEY"].encode("utf-8"), raw, hashlib.sha256).hexdigest()


def receive(req):
    raw = req["raw"]
    if req["headers"].get("Content-Encoding") == "gzip":
        raw = zlib.decompress(raw, 16 + zlib.MAX_WBITS)
    if not hmac.compare_digest(req["headers"].get("X-Chu-Ky", ""), _signature(raw)):
        raise Denied(401, "sai chu ky")
    event = json.loads(raw)
    event_id, invoice_id, amount = str(event["ma_su_kien"]), int(event["hoa_don"]), int(event["so_tien"])
    with db.tx() as conn:
        cur = conn.execute(
            "INSERT OR IGNORE INTO payments (event_id, invoice_id, amount, at) VALUES (?, ?, ?, ?)",
            (event_id, invoice_id, amount, int(time.time())),
        )
        if cur.rowcount == 1:
            conn.execute(
                "UPDATE invoices SET status = 'paid' WHERE id = ? AND status = 'issued' AND amount <= ?",
                (invoice_id, amount),
            )
    return 200, {"ok": True}
