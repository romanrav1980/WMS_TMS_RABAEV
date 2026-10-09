import json
from pathlib import Path
p=Path("WindowsApplication2/WindowsApplication2/Form1.cs");s=p.read_text(encoding="utf-8")
needle='values["BRT_KOR"] = BRT_KOR;\n\n                object ret = wms_get_spfunction_value2("ARTICULS.UPDATE_MOD", values, OracleType.Int32, 0);'
assert needle in s
s=s.replace(needle,'values["BRT_KOR"] = BRT_KOR;\n                values["p_actor"] = this.wms_user.user_id;\n\n                object ret = wms_get_spfunction_value2("ARTICULS.UPDATE_MOD", values, OracleType.Int32, 0);',1)
needle='''                if (ID == 0)
                {
                    ID = obj2int(ret);
                }
                dataGridView25.CurrentRow.Cells[0].Value = ID;'''
assert needle in s;s=s.replace(needle,'''                ID = obj2int(ret);
                dataGridView25.CurrentRow.Cells[0].Value = ID;''',1)
print(json.dumps({str(p):s},ensure_ascii=True))
