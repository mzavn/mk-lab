MEMBER_FIELDS = ("id", "name", "email", "role", "locked")
INVOICE_FIELDS = ("id", "project_id", "customer_name", "amount", "status", "period", "issued_at")
PUBLIC_INVOICE_FIELDS = ("id", "customer_name", "amount", "status", "issued_at")


def pick(row, fields):
    return {field: row[field] for field in fields}


def member(row):
    return pick(row, MEMBER_FIELDS)


def invoice(row):
    return pick(row, INVOICE_FIELDS)


def public_invoice(row):
    return pick(row, PUBLIC_INVOICE_FIELDS)
