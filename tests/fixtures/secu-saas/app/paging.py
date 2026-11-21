DEFAULT_ROWS = 20
MAX_ROWS = 50
MAX_PAGE = 1000


def window(query):
    rows = min(max(int(query.get("so_dong", DEFAULT_ROWS)), 1), MAX_ROWS)
    page = min(max(int(query.get("trang", 1)), 1), MAX_PAGE)
    return rows, (page - 1) * rows
