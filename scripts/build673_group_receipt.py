import json
from pathlib import Path
s=Path("scripts/case412_group_receipt.py").read_text(encoding="utf-8").replace("412","673").replace("406","671")
old="scans=[code for ctx in(first,second)for unit in ctx['units']for code in unit['codes']])"
new="""scans=[code for unit in first['units']for code in unit['codes']if code['system_code']=='CRPT'],
 aggregation_scans=[dict(system_code='EGAIS',profile_code='ALCOHOL',level='BOX',code='EGAIS.B:'+first['tag']),dict(system_code='CRPT',profile_code='TOBACCO',level='PALLET',code=second['lot'])])"""
assert old in s;s=s.replace(old,new)
anchor="if 'group_receipt'not in saved:\n with oracledb.connect"
negative="""if 'group_receipt'not in saved:
 from copy import deepcopy
 from app.modules.inventory.contracts_stock import StockPostingError
 cases=[]
 fallback=deepcopy(meta);fallback['scans'] += [code for unit in second['units']for code in unit['codes']]
 cases.append(('unit_fallback',fallback,'INTERWARE_GROUP_AGGREGATE_ONLY_UNIT_FALLBACK_FORBIDDEN'))
 wrong=deepcopy(meta);wrong['aggregation_scans'][1]['code']='WRONG:'+tag;cases.append(('wrong_code',wrong,None))
 missing=deepcopy(meta);missing['aggregation_scans']=missing['aggregation_scans'][:1];cases.append(('incomplete',missing,None))
 quantity=deepcopy(meta);quantity['items'][1]['quantity']='2';cases.append(('quantity',quantity,'INTERWARE_GROUP_EXACT_ITEM_REQUIRED'))
 for label,bad,reason in cases:
  try:svc.receive_action('INTERWARE_RECEIVE','GROUP673.BAD:'+label+':'+tag,saved['group_plan_operation_id'],bad,'admin');raise AssertionError('Expected refusal '+label)
  except StockPostingError as e:
   if reason:assert reason in str(e.rule_reason or e),str(e)
 saved['aggregation_negative_cases']=[label for label,_,_ in cases];p.write_text(json.dumps(saved,indent=2),encoding='utf-8')
 with oracledb.connect"""
assert anchor in s;s=s.replace(anchor,negative)
s=s.replace("PASS673", "PASS673")
print(json.dumps({"scripts/case673_group_receipt.py":s}))
