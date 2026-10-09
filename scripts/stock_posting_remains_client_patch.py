import json
from pathlib import Path
out={}
p=Path("WindowsApplication2/WindowsApplication2/Form1.cs");s=p.read_text(encoding="utf-8")
at=s.index("public object wms_get_spfunction_value2(");end=s.index("public string wms_get_spfunction_value(",at)
part=s[at:end]
needle='''                int rowsAffected = ora_com.ExecuteNonQuery();
                object ret1 = (ora_com.Parameters["ret"].Value);
                return ret1;'''
assert needle in part
part=part.replace(needle,'''                StockCommandIntent moveIntent = null;
                if (String.Equals(spf, "REMAINS.move_pall_2_picking_cell", StringComparison.OrdinalIgnoreCase))
                    moveIntent = StockCommandIntent.Prepare(ora_com, wms_user.user_id, obj2str(values["pall_uid1"]));
                int rowsAffected = ora_com.ExecuteNonQuery();
                object ret1 = (ora_com.Parameters["ret"].Value);
                if (moveIntent != null && obj2str(ret1).StartsWith("ok", StringComparison.Ordinal)) moveIntent.Confirm();
                return ret1;''',1)
s=s[:at]+part+s[end:];out[str(p)]=s
for filename in ("180_remains_adapter.sql","067_internal_entrypoints.sql"):
 p=Path("db/migrations/2026-10-08_stock_posting_core")/filename;s=p.read_text(encoding="utf-8")
 if filename.startswith("180"):
  s=s.replace("m.put('uid',pall_uid1);","m.put_null('unit');m.put('uid',pall_uid1);",1)
 else:
  s=s.replace("m.put('uid',pallet_id);","m.put_null('unit');m.put('uid',pallet_id);",1)
 out[str(p)]=s
print(json.dumps(out,ensure_ascii=True))
