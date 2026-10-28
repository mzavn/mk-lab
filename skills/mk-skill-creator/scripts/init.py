#!/usr/bin/env python3
"""Tạo khung một skill mới của bộ mk: <thư mục skills>/mk-<tên>/SKILL.md từ assets/SKILL.md.template.

Cách gọi: python3 init.py <tên> --path <thư mục skills>
  <tên>  chữ thường, số, gạch nối giữa các phần (vd ghi-chu) — không kèm tiền tố mk- hay mk:
Không ghi đè: thư mục đích đã có (kể cả là file hay symlink) → Lỗi, thoát 1. Không ghi xuyên symlink.
Thoát 0 khi tạo xong; 1 khi lỗi (dòng "Lỗi: …", không để lại file dở).
"""
import argparse
import os
import re
import shutil
import sys

sys.dont_write_bytecode = True

HERE = os.path.dirname(os.path.abspath(__file__))
TEMPLATE = os.path.join(os.path.dirname(HERE), "assets", "SKILL.md.template")
NAME_RE = re.compile(r"[a-z0-9]+(-[a-z0-9]+)*")


class Fail(Exception):
    pass


class Parser(argparse.ArgumentParser):
    def error(self, message):
        print(f"Lỗi: {message}\n{self.format_usage().strip()}")
        sys.exit(1)


def check_name(name):
    if name.startswith(("mk-", "mk:")):
        raise Fail(f"tên '{name}' đã có tiền tố — chỉ đưa phần sau, vd '{name[3:]}'")
    if not NAME_RE.fullmatch(name):
        raise Fail(f"tên '{name}' không hợp lệ — chỉ chữ thường a-z, số, gạch nối giữa các phần (vd ghi-chu)")


def check_parent(path):
    if os.path.islink(path):
        raise Fail(f"{path} là symlink — không ghi xuyên symlink, đưa đường dẫn thật")
    if not os.path.exists(path):
        raise Fail(f"không có thư mục {path}")
    if not os.path.isdir(path):
        raise Fail(f"{path} không phải thư mục")


def create(name, parent):
    check_name(name)
    parent = parent.rstrip(os.sep) or os.sep  # "link/" làm lstat đi theo symlink — bỏ "/" cuối trước khi kiểm
    check_parent(parent)
    target = os.path.join(parent, f"mk-{name}")
    if os.path.lexists(target):
        raise Fail(f"{target} đã có — không ghi đè")
    with open(TEMPLATE, encoding="utf-8") as fh:
        text = fh.read().replace("{{TEN}}", name)
    try:
        os.mkdir(target)
    except FileExistsError:
        raise Fail(f"{target} đã có — không ghi đè")
    try:
        with open(os.path.join(target, "SKILL.md"), "x", encoding="utf-8") as fh:
            fh.write(text)
    except BaseException:
        shutil.rmtree(target, ignore_errors=True)  # chỉ thư mục vừa tạo ở trên
        raise
    return target


def main(argv):
    ap = Parser(prog="init.py", description="Tạo khung skill mk-<tên>.")
    ap.add_argument("name", metavar="<tên>")
    ap.add_argument("--path", required=True, metavar="<thư mục skills>")
    args = ap.parse_args(argv)
    try:
        target = create(args.name, args.path)
    except Fail as e:
        print(f"Lỗi: {e}")
        return 1
    except OSError as e:
        print(f"Lỗi: không ghi được — {e.strerror or e}")
        return 1
    print(f"Đã tạo: {target}")
    print("Tiếp theo: điền mọi chỗ {{…}} trong SKILL.md; viết script + test trước (scripts/, scripts/tests/), "
          "references/ sau; rồi chạy:")
    print(f"  python3 {os.path.join(HERE, 'validate.py')} {target}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
