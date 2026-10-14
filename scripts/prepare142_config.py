from pathlib import Path
import json
out={}
source=Path("db/migrations/2026-10-08_stock_posting_core/047_configuration.sql").read_text(encoding="utf-8-sig")
out["db/migrations/2026-10-08_stock_posting_core/447_config_before_topology.sql"]=source
out["db/migrations/2026-10-10_ni081_pickface_config/001_config.sql"]=source.replace("'warehouse_settings_edit','finished_goods_edit','sap_article_import'","'warehouse_settings_edit','finished_goods_edit','sap_article_import','pick_topology_edit'")
print(json.dumps(out,ensure_ascii=True))
