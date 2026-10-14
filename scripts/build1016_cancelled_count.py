from pathlib import Path
import json
files={}
p="api/wms_api_server/app/modules/fulfillment/domain/execution_progress.py";v=Path(p).read_text(encoding="utf-8").replace('def order_progress_status(lines:', 'def line_is_cancelled(line: dict[str, Any]) -> bool:\n    return line.get("row_status") == "CANCELLED" or line["status"] == "CANCELLED"\n\n\ndef order_progress_status(lines:',1).replace('active = [line for line in lines if line["status"] != "CANCELLED"]','active = [line for line in lines if not line_is_cancelled(line)]',1);files[p]=v
p="api/wms_api_server/app/modules/fulfillment/infrastructure/execution_progress.py";v=Path(p).read_text(encoding="utf-8").replace('line_progress, order_progress_status','line_progress, order_progress_status, line_is_cancelled',1).replace('sum(line["status"] != "CANCELLED" for line in lines)','sum(not line_is_cancelled(line) for line in lines)',1);files[p]=v
p="wiki-raw/wms_admin_ui_reference/order-execution.js";v=Path(p).read_text(encoding="utf-8").replace('line.status==="CANCELLED"?"— (отменено)"','(line.status==="CANCELLED"||line.row_status==="CANCELLED")?"— (отменено)"',1);files[p]=v
print(json.dumps(files,ensure_ascii=True))
