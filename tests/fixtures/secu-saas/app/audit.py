import json
import time

import db

REDACTED = {"mat_khau", "mat_khau_cu", "mat_khau_moi", "otp", "token", "ma_xac_nhan"}


def record(actor, action, data):
    safe = {key: ("***" if key in REDACTED else value) for key, value in data.items()}
    db.run(
        "INSERT INTO audit_log (company_id, user_id, action, data, at) VALUES (?, ?, ?, ?, ?)",
        (actor["company_id"], actor["id"], action, json.dumps(safe, ensure_ascii=False), int(time.time())),
    )
