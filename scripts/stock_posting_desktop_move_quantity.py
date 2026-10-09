"""Keep exact decimal input and never interpret malformed text as whole-pallet zero."""
import json,re
from pathlib import Path
p=Path("WindowsApplication2/WindowsApplication2/Form1.cs")
s=p.read_text(encoding="utf-8")
pattern=r"(?m)^(\s*)long iiii = 0;\s*try\s*\{\s*iiii = Convert.ToInt64\(СКОЛЬКО_ПЕРЕМЕЩАЕМ.Text\);\s*\}\s*catch \{ \}"
def replacement(m):
 indent=m.group(1)
 return indent+"decimal iiii;\n"+indent+"""if (!decimal.TryParse(СКОЛЬКО_ПЕРЕМЕЩАЕМ.Text.Trim().Replace(',', '.'),
"""+indent+"""    System.Globalization.NumberStyles.AllowDecimalPoint,
"""+indent+"""    System.Globalization.CultureInfo.InvariantCulture, out iiii) || iiii < 0)
"""+indent+"""{
"""+indent+"""    MessageBox.Show("Укажите корректное количество; 0 — переместить всю паллету.");
"""+indent+"""    return;
"""+indent+"}"
s,n=re.subn(pattern,replacement,s)
assert n==2,n
needle='                ora_com.Parameters.Add("iser_id21", OracleType.VarChar).Value = wms_user.user_id;\n                ora_com.Parameters.Add("ret",'
assert s.count(needle)==1
s=s.replace(needle,'                ora_com.Parameters.Add("iser_id21", OracleType.VarChar).Value = wms_user.user_id;\n                StockCommandIntent shipmentIntent = StockCommandIntent.Prepare(ora_com, wms_user.user_id, order_id.ToString(System.Globalization.CultureInfo.InvariantCulture));\n                ora_com.Parameters.Add("ret",',1)
needle='                rrr = rrr + ora_com.Parameters["ret"].Value.ToString();'
assert s.count(needle)==1
s=s.replace(needle,'                string shipmentResult = ora_com.Parameters["ret"].Value.ToString();\n                if (shipmentResult.StartsWith("ok", StringComparison.Ordinal)) shipmentIntent.Confirm();\n                rrr = rrr + shipmentResult;',1)
print(json.dumps({str(p):s},ensure_ascii=True))
