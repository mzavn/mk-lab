import hashlib
import html
import json


def escaped(row):
    return {key: html.escape(str(value), quote=True) for key, value in row.items()}


def send(handler, status, payload, headers=()):
    if isinstance(payload, str):
        data = payload.encode("utf-8")
        kind = "text/html; charset=utf-8"
    else:
        data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        kind = "application/json"
    handler.send_response(status)
    handler.send_header("Content-Type", kind)
    handler.send_header("Content-Length", str(len(data)))
    handler.send_header("ETag", '"' + hashlib.sha256(data).hexdigest()[:32] + '"')
    handler.send_header("X-Content-Type-Options", "nosniff")
    for name, value in headers:
        handler.send_header(name, value)
    handler.end_headers()
    handler.wfile.write(data)
