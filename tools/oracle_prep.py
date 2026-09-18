#!/usr/bin/env python3
"""Oracle DDL → tree-sitter-sql 解析得動的形式。
只動型別名稱、型別參數、實體儲存子句；不碰表名、欄位名、約束、FK。
用法: python3 oracle_prep.py < in.sql > out.sql"""
import re, sys

# ① Oracle 專有型別 → ANSI（tree-sitter-sql 不認得 VARCHAR2 等）
TYPE_MAP = [
    (r'\bVARCHAR2\b', 'VARCHAR'), (r'\bNVARCHAR2\b', 'VARCHAR'),
    (r'\bNUMBER\b', 'NUMERIC'),   (r'\bCLOB\b', 'TEXT'),
    (r'\bNCLOB\b', 'TEXT'),       (r'\bBLOB\b', 'BYTEA'),
    (r'\bRAW\b', 'BYTEA'),        (r'\bBINARY_DOUBLE\b', 'DOUBLE'),
    (r'\bBINARY_FLOAT\b', 'FLOAT'),
]
# ② 型別參數（含 BYTE/CHAR 長度語意）一律拿掉
TYPE_ARGS = re.compile(
    r'\b(VARCHAR|NUMERIC|TEXT|BYTEA|DOUBLE|FLOAT|DECIMAL|CHAR|TIMESTAMP)\s*\([^)]*\)', re.I)
# ③ 結尾的實體儲存子句
STORAGE = re.compile(
    r'\s*(?:SEGMENT\s+CREATION\s+(?:IMMEDIATE|DEFERRED)'
    r'|PCTFREE|PCTUSED|INITRANS|MAXTRANS|NOCOMPRESS|COMPRESS|LOGGING|NOLOGGING'
    r'|TABLESPACE|STORAGE\s*\([^)]*\)|PARALLEL|NOPARALLEL|CACHE|NOCACHE|MONITORING'
    r'|ORGANIZATION\s+\w+|PARTITION\s+BY)\b[^;]*(?=;)', re.I)

def clean(sql: str) -> str:
    for pat, repl in TYPE_MAP:
        sql = re.sub(pat, repl, sql, flags=re.I)
    sql = TYPE_ARGS.sub(lambda m: m.group(1), sql)
    sql = STORAGE.sub('', sql)
    return sql

if __name__ == "__main__":
    sys.stdout.write(clean(sys.stdin.read()))
