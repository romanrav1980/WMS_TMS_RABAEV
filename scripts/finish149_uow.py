from pathlib import Path
import ast,json
p=Path("api/wms_api_server/app/modules/inventory/infrastructure/stock_posting_uow.py");text=p.read_text(encoding="utf-8")
start=text.index("        birth_captures = {}");end=text.index("        posting_started = True",start)
block=text[start:end]
helper='''"""Pure hints/captures on the posting cursor; root alone decides immutable replay."""
import json
from typing import Any
import oracledb

def prepare_staging_inputs(cursor: oracledb.Cursor,command_document: dict[str,Any],
                           operation_id: str) -> tuple[str|None,dict[str,Any],dict[str,Any]|None]:
'''
helper+="".join(line[4:]if line.startswith("    ")else line for line in block.splitlines(keepends=True))
helper+="    return resolution,birth_captures,receipt_marks\n"
ast.parse(helper)
text=text[:start]+"        resolution,birth_captures,receipt_marks=prepare_staging_inputs(cursor,command_document,operation_id)\n"+text[end:]
text=text.replace("from ..contracts_stock import StockCommand, StockPostingError","from ..contracts_stock import StockCommand, StockPostingError\nfrom .stock_staging_inputs import prepare_staging_inputs")
ast.parse(text)
print(json.dumps({str(p):text,str(p.with_name("stock_staging_inputs.py")):helper},ensure_ascii=True))
