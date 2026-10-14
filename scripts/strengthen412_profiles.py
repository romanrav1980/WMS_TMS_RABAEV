from pathlib import Path
import json
p=Path('db/migrations/2026-10-12_ni061_group_receive/003_core.sql');t=p.read_text(encoding='utf-8')
needle="item.put('uom_version',v_version);lots.put(i,item,true);"
replacement="""select count(*)into n from RRL_SKU_RECEIPT_PROFILE where ARTICUL=v_article;
  if n>0 then
   declare matched number;begin
    select count(*)into matched from RRL_WMS_RECEIPT_UNIT u join RRL_WMS_RECEIPT_CODE code on code.UID_PALLET=u.UID_PALLET and code.UNIT_ID=u.UNIT_ID
    join RRL_SKU_RECEIPT_PROFILE card on card.ARTICUL=v_article and card.SYSTEM_CODE=code.SYSTEM_CODE,
    json_table(code.PROFILES_JSON,'$[*]'columns(CODE_PROFILE varchar2(80)path '$.profile',CODE_VERSION varchar2(40)path '$.version'))decoded
    where u.CURRENT_UID=v_uid and u.STOCK_STATUS='ISSUED'and card.PROFILE_CODE=decoded.CODE_PROFILE and card.PROFILE_VERSION=decoded.CODE_VERSION;
    if matched!=n*manifest.get_number('physical_unit_count')then raise_application_error(-20886,'INTERWARE_GROUP_CURRENT_CODE_PROFILE_VERSION_REQUIRED');end if;
   end;
  end if;
  """+needle
assert needle in t;t=t.replace(needle,replacement,1)
print(json.dumps({p.as_posix():t}))
