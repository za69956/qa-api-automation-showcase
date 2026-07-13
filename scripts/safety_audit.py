#!/usr/bin/env python3
from pathlib import Path
import re
import sys

bad_file_suffixes = {".db", ".sqlite", ".sqlite3", ".env"}
bad_file_names = {"crypto.db", ".env"}

content_patterns = {
    "PRIVATE_WINDOWS_USER_PATH": re.compile(r"C:\\Users\\[^\\\s]+", re.I),
    "PRIVATE_GIT_BASH_USER_PATH": re.compile(r"/c/Users/[^/\s]+", re.I),
    "REAL_SECRET_ASSIGNMENT": re.compile(
        r"(api[_-]?key|secret|token|password)\s*[:=]\s*['\"][A-Za-z0-9_\-]{12,}",
        re.I,
    ),
    "AUTHORIZATION_BEARER": re.compile(
        r"Authorization:\s*Bearer\s+[A-Za-z0-9_\-\.]{12,}",
        re.I,
    ),
    "LIVE_ORDER_CALL": re.compile(
        r"create_order\(|place_order\(|market_order\(|limit_order\(",
        re.I,
    ),
}

skip_files = {"scripts/safety_audit.py"}
skip_parts = {
    "__pycache__",
    ".git",
    ".pytest_cache",
    ".venv",
    "venv",
}

hits = []

for p in Path(".").rglob("*"):
    if p.is_dir():
        continue

    if any(part in skip_parts for part in p.parts):
        continue

    rel = p.as_posix().lstrip("./")
    if rel in skip_files:
        continue

    if p.name in bad_file_names or p.suffix.lower() in bad_file_suffixes:
        hits.append((str(p), "SENSITIVE_FILE"))
        continue

    text = p.read_text(encoding="utf-8", errors="ignore")
    for label, pattern in content_patterns.items():
        if pattern.search(text):
            hits.append((str(p), label))

if hits:
    print("QA_SHOWCASE_AUDIT_FAIL")
    for path, label in hits:
        print(f"{path}: {label}")
    sys.exit(1)

print("QA_SHOWCASE_AUDIT_PASS")
