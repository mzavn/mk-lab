from web import Denied

OWNER = ("owner",)
FINANCE = ("owner", "accountant")
MANAGERS = ("owner", "manager")
DRAFTERS = ("owner", "accountant", "manager")
ASSIGNABLE = ("manager", "accountant", "member")


def require(user, allowed):
    if user["role"] not in allowed:
        raise Denied(403, "khong co quyen")
