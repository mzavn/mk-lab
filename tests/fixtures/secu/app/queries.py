PAGE_SIZE = 20


def recent_orders_sql(page):
    offset = (page - 1) * PAGE_SIZE
    return (
        "SELECT id, title, total, status, created_at FROM orders WHERE owner_id = ? "
        f"ORDER BY created_at DESC LIMIT {PAGE_SIZE} OFFSET {offset}"
    )
