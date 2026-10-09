"""Reuse the authorized local serv.bat Oracle defaults without logging credentials."""
import os
import re
from pathlib import Path


def load_local_oracle_environment():
    script=(Path(__file__).resolve().parents[1]/"serv.bat").read_text(encoding="utf-8-sig")
    for key in ("WMS_ORACLE_USER","WMS_ORACLE_PASSWORD","WMS_ORACLE_DSN"):
        match=re.search(r'if not defined '+key+r' set "'+key+r'=([^"]*)"',script,re.I)
        if match and "%" not in match.group(1):
            os.environ.setdefault(key,match.group(1))
