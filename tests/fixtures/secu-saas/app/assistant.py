import billing
import confirmations
import db
import members
import roles
import views


def tool_find_invoices(actor, args):
    rows = db.all_rows(
        "SELECT * FROM invoices WHERE company_id = ? AND customer_name LIKE ? ORDER BY id DESC LIMIT 20",
        (actor["company_id"], "%" + str(args.get("khach", ""))[:100] + "%"),
    )
    return [views.invoice(row) for row in rows]


def tool_refund(actor, args):
    roles.require(actor, roles.FINANCE)
    if not args.get("da_xac_nhan"):
        return {"can_xac_nhan": True, "thong_diep": "hoi nguoi dung truoc khi hoan tien"}
    return billing.refund(actor, int(args["hoa_don"]), int(args["so_tien"]))


def tool_change_role(actor, args):
    roles.require(actor, roles.OWNER)
    content = {"thanh_vien": int(args["thanh_vien"]), "vai": str(args["vai"])}
    confirmations.consume(actor, "doi-vai", str(args.get("ma_xac_nhan", "")), content)
    return members.apply_role(actor, content["thanh_vien"], content["vai"])


TOOLS = {
    "tim_hoa_don": tool_find_invoices,
    "hoan_tien": tool_refund,
    "doi_vai": tool_change_role,
}


def call_tool(req):
    tool = TOOLS.get(str(req["body"].get("tool", "")))
    if tool is None:
        return 404, {"loi": "khong co tool nay"}
    args = req["body"].get("args") or {}
    if not isinstance(args, dict):
        raise ValueError("args")
    return 200, {"ket_qua": tool(req["user"], args)}
