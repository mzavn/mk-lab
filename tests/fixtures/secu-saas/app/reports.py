import db
import periods
import projects
import roles


def _company(req):
    return int(req["headers"].get("X-Cong-Ty") or req["user"]["company_id"])


def revenue(req):
    roles.require(req["user"], roles.FINANCE)
    period = periods.parse(req["query"].get("ky", ""))
    rows = db.all_rows(
        "SELECT p.name AS du_an, SUM(i.amount) AS doanh_thu FROM invoices i "
        "JOIN projects p ON p.id = i.project_id "
        "WHERE i.company_id = ? AND i.period = ? AND i.status IN ('issued', 'paid') "
        "GROUP BY p.id ORDER BY p.name",
        (_company(req), period),
    )
    return 200, {"ky": period, "dong": rows}


def project_lines(req):
    project = projects.load_in_company(req["user"]["company_id"], int(req["query"].get("du_an", 0)))
    rows = db.all_rows(
        "SELECT i.id AS hoa_don, l.description, l.quantity, l.unit_price FROM invoice_lines l "
        "JOIN invoices i ON i.id = l.invoice_id "
        "WHERE i.project_id = ? AND i.status IN ('issued', 'paid') ORDER BY i.id, l.id",
        (project["id"],),
    )
    return 200, {"du_an": project["name"], "dong": rows}
