import re

import db
import roles
from web import Denied

PERIOD = re.compile(r"\d{4}-(0[1-9]|1[0-2])")


def parse(value):
    value = str(value)
    if not PERIOD.fullmatch(value):
        raise ValueError("ky")
    return value


def ensure_open(company_id, period):
    row = db.one("SELECT closed FROM periods WHERE company_id = ? AND period = ?", (company_id, period))
    if row and row["closed"]:
        raise Denied(409, "ky da chot")


def close(req):
    user = req["user"]
    roles.require(user, roles.OWNER)
    period = parse(req["body"]["ky"])
    db.run(
        "INSERT INTO periods (company_id, period, closed) VALUES (?, ?, 1) "
        "ON CONFLICT (company_id, period) DO UPDATE SET closed = 1",
        (user["company_id"], period),
    )
    return 200, {"ok": True}
