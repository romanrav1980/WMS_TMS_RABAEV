import json
from pathlib import Path
D=Path("db/migrations/2026-10-08_stock_posting_core");out={}
p=D/"018_balances.sql";s=p.read_text(encoding="utf-8")
needle=" procedure apply_delta(p_uid varchar2,p_cell varchar2,p_delta_p number,p_delta_h number,"
at=s.index(needle,s.index("create or replace package body"))
method=""" procedure freeze_pack(p_uid varchar2,p_base varchar2) is
  v_frozen number;v_factor number;v_mod number;v_article varchar2(160);v_base varchar2(20);
 begin
  RRL_STOCK_LOCK_API.assert_held(30,RRL_STOCK_LOCK_API.resource_key('HU',p_uid));
  select STOCK_PACK_FROZEN,STOCK_BOX_FACTOR,MOD_ID,ARTICUL,STOCK_PACK_BASE_UOM into v_frozen,v_factor,v_mod,v_article,v_base
   from RRL_PALLETS where UID_PALLET=p_uid;
  if v_frozen=1 then
   if v_base!=p_base then raise_application_error(-20887,'PALLET_PACK_BASE_CONFLICT');end if;
   return;
  end if;
  v_factor:=null;
  if upper(p_base) in('EA','PCS','ST',unistr('\\0428\\0422')) then
   if nvl(v_mod,0)>0 then
    select SHT_IN_KOR into v_factor from RRL_ARTICUL_MODS where ID=v_mod and ARTICUL=v_article;
   else
    select COUNT_SHT_IN_KOR into v_factor from RRL_ARTICULS where ACTICUL=v_article;
   end if;
   if v_factor is null or v_factor<1 or v_factor!=trunc(v_factor) or v_factor>1000000000 then v_factor:=null;end if;
  end if;
  update RRL_PALLETS set STOCK_BOX_FACTOR=v_factor,STOCK_PACK_BASE_UOM=p_base,STOCK_PACK_FROZEN=1 where UID_PALLET=p_uid;
 end;
"""
s=s[:at]+method+s[at:]
needle="  RRL_STOCK_CTX_API.begin_effect('STOCK',p_uid,p_cell);"
assert needle in s;s=s.replace(needle,"  if p_delta_p>0 then freeze_pack(p_uid,p_base_uom);end if;\n"+needle,1)
out[str(p)]=s
p=D/"062_pallet_uom.sql";s=p.read_text(encoding="utf-8")
needle="   if nvl(p.MOD_ID,0)!=0 then"
at=s.index(needle);end=s.index("   if v_pack is null",at)
s=s[:at]+"""   if p.STOCK_PACK_FROZEN=1 then
    if p.STOCK_PACK_BASE_UOM!=p_base then raise_application_error(-20887,'PALLET_PACK_BASE_CONFLICT');end if;
    v_pack:=p.STOCK_BOX_FACTOR;v_provenance:='PALLET.FROZEN_PACK';
   else
    -- A lot already in stock must never silently adopt a later article factor.
    select count(*) into v_pack from RRL_REMAINS where UID_POLETA=p_uid and REMAIN>0;
    if v_pack>0 then raise_application_error(-20887,'PALLET_PACK_SNAPSHOT_REQUIRED');end if;
    if nvl(p.MOD_ID,0)!=0 then
     select SHT_IN_KOR into v_pack from RRL_ARTICUL_MODS where ID=p.MOD_ID and ARTICUL=p.ARTICUL;
     v_provenance:='PALLET.MOD_ID';
    else
     select COUNT_SHT_IN_KOR into v_pack from RRL_ARTICULS where ACTICUL=p.ARTICUL;
     v_provenance:='ARTICLE.DEFAULT_PACK_BEFORE_ADMISSION';
    end if;
   end if;
"""+s[end:]
out[str(p)]=s
print(json.dumps(out,ensure_ascii=True))
