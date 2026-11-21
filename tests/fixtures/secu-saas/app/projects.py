import db
import roles
from web import Denied

MAX_BUDGET = 10**12


def load_in_company(company_id, project_id):
    row = db.one("SELECT * FROM projects WHERE id = ? AND company_id = ?", (project_id, company_id))
    if row is None:
        raise Denied(404, "khong tim thay")
    return row


def _budget(value):
    budget = int(value)
    if not 0 <= budget <= MAX_BUDGET:
        raise ValueError("ngan sach")
    return budget


def _insert(company_id, name):
    name = str(name).strip()[:120]
    if not name:
        raise ValueError("ten")
    with db.tx() as conn:
        cur = conn.execute(
            "INSERT INTO projects (company_id, name, budget, status) VALUES (?, ?, 0, 'active')",
            (company_id, name),
        )
    return cur.lastrowid


def list_projects(req):
    rows = db.all_rows(
        "SELECT id, name, budget, status FROM projects WHERE company_id = ? ORDER BY name",
        (req["user"]["company_id"],),
    )
    return 200, {"du_an": rows}


def create_project(req):
    return 201, {"ma": _insert(req["user"]["company_id"], req["body"]["ten"])}


def copy_project(req):
    user = req["user"]
    source = load_in_company(user["company_id"], int(req["body"]["ma"]))
    return 201, {"ma": _insert(user["company_id"], source["name"] + " (ban sao)")}


def update_budget(req):
    user = req["user"]
    roles.require(user, roles.MANAGERS)
    project = load_in_company(user["company_id"], int(req["body"]["ma"]))
    if project["status"] != "active":
        raise Denied(409, "du an da luu tru")
    db.run("UPDATE projects SET budget = ? WHERE id = ?", (_budget(req["body"]["ngan_sach"]), project["id"]))
    return 200, {"ok": True}


def bulk_budgets(req):
    user = req["user"]
    items = req["body"]["du_an"]
    if not isinstance(items, list) or not 0 < len(items) <= 200:
        raise ValueError("du an")
    changes = [(_budget(item["ngan_sach"]), int(item["ma"])) for item in items]
    with db.tx() as conn:
        for budget, project_id in changes:
            cur = conn.execute(
                "UPDATE projects SET budget = ? WHERE id = ? AND company_id = ? AND status = 'active'",
                (budget, project_id, user["company_id"]),
            )
            if cur.rowcount != 1:
                raise Denied(404, "khong tim thay")
    return 200, {"so_du_an": len(changes)}


def archive_project(req):
    user = req["user"]
    roles.require(user, roles.MANAGERS)
    project = load_in_company(user["company_id"], int(req["body"]["ma"]))
    db.run("UPDATE projects SET status = 'archived' WHERE id = ?", (project["id"],))
    return 200, {"ok": True}
