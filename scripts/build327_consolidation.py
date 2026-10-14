from pathlib import Path
import json,re
d=Path("db/migrations/2026-10-12_ni061_ordinary_consolidation");out={}
def put(n,s):out[(d/n).as_posix()]=s
schema="""declare v_name varchar2(128);v_cols varchar2(500);begin
 select c.CONSTRAINT_NAME,listagg(cc.COLUMN_NAME,',')within group(order by cc.POSITION)into v_name,v_cols from USER_CONSTRAINTS c join USER_CONS_COLUMNS cc on cc.CONSTRAINT_NAME=c.CONSTRAINT_NAME where c.TABLE_NAME='RRL_INTERWARE_ONWARD_DISPATCH'and c.CONSTRAINT_TYPE='P'group by c.CONSTRAINT_NAME;
 if v_cols='OPERATION_ID'then
  execute immediate 'alter table RRL_INTERWARE_ONWARD_DISPATCH drop constraint '||dbms_assert.simple_sql_name(v_name);
  execute immediate 'alter table RRL_INTERWARE_ONWARD_DISPATCH add constraint RRL_IW_ONWARD_DISPATCH_PK primary key(OPERATION_ID,ST_ID)';
 elsif v_cols!='OPERATION_ID,ST_ID'then raise_application_error(-20899,'UNEXPECTED_ONWARD_DISPATCH_PRIMARY_KEY');end if;
end;
/
"""
put("001_schema.sql",schema)
for name,file in [("RRL_STOCK_HU_SHIP_CMD","002_shipping.sql"),("RRL_STOCK_INTERWARE_NEXT","003_next.sql"),("RRL_INTERWARE_DEPART_GATE","004_depart.sql")]:
 old=Path("tmp/327_"+name.lower()+".sql").read_text(encoding="utf-8");put("000_before_"+name.lower()+".sql",old);new=old
 if name=="RRL_STOCK_HU_SHIP_CMD":
  start=new.index("   if subdomain.has('interwarehouse_onward_source')and(")
  stop=new.index("  end loop;",start)
  new=new[:start]+"""   if subdomain.has('interwarehouse_onward_source')and(plans.get_size!=1 or expected_qty.count!=1)then
    if subdomain.get_object('interwarehouse_onward_source').has('recovery_operation_id')then raise_application_error(-20886,'INTERWARE_MULTI_RECOVERY_EXPLICIT_LINEAGE_REQUIRED');end if;
    for t in(select UID_VALUE,ARTICLE_VALUE,KIND_VALUE from json_table(nodes,'$[*]'columns(UID_VALUE varchar2(200)path '$.uid',ARTICLE_VALUE varchar2(160)path '$.article',KIND_VALUE varchar2(20)path '$.kind')))loop
     if t.KIND_VALUE not in('CONTAINER','STOCK')then raise_application_error(-20886,'INTERWARE_CONSOLIDATED_STOCK_ONLY_REQUIRED');end if;
     if t.KIND_VALUE='STOCK'then
      select count(*)into leg_count from dual where exists(select 1 from RRL_WMS_RECEIPT_UNIT where CURRENT_UID=t.UID_VALUE)
       or exists(select 1 from RRL_SKU_RECEIPT_PROFILE where ARTICUL=t.ARTICLE_VALUE)
       or exists(select 1 from RRL_SKU_RECEIPT_POLICY where ARTICUL=t.ARTICLE_VALUE and MARKING_REQUIRED=1)
       or exists(select 1 from RRL_FINISHED_GOODS_SKU where ARTICUL=t.ARTICLE_VALUE and CRPT_REQUIRED=1);
      if leg_count!=0 then raise_application_error(-20886,'INTERWARE_CONSOLIDATED_MARKED_MATRIX_REQUIRED');end if;
     end if;
    end loop;
   end if;
"""+new[stop:]
 elif name=="RRL_STOCK_INTERWARE_NEXT":
  new=new.replace("utl_i18n.string_to_raw(op,'AL32UTF8')","utl_i18n.string_to_raw(op||':'||RRL_STOCK_PLAN_HELPER.decimal_text(v_st),'AL32UTF8')")
 else:
  pattern=r"\s*and\(select count\(\*\)from json_table\(l.COMPOSITION_JSON,'\$\.nodes\[\*\]'columns\(\s*K varchar2\(20\)path '\$\.kind',U varchar2\(200\)path '\$\.uid',Q varchar2\(60\)path '\$\.quantity'\)\)archive\s*where archive.K='STOCK'\)=1"
  new,n=re.subn(pattern,"",new);assert n==1
 assert new!=old,name
 put(file,new)
put("005_recompile.sql",Path("db/migrations/2026-10-12_ni061_nested_receiving/009_recompile.sql").read_text(encoding="utf-8"))
put("006_ledger.sql","merge into RRL_SCHEMA_MIGRATIONS t using(select '2026-10-12-327-ordinary-onward-consolidation' MIGRATION_ID from dual)s on(t.MIGRATION_ID=s.MIGRATION_ID)when not matched then insert(MIGRATION_ID,DESCRIPTION,APPLIED_AT,APPLIED_BY,SCRIPT_NAME,ROLLBACK_SCRIPT,STATUS)values(s.MIGRATION_ID,'One physical upperHU carries multiple exact ordinary onward ST leaves with per-ST immutable dispatch and outgoing identities',sysdate,user,'apply.sql','rollback.sql','APPLIED');\ncommit;\n")
put("apply.sql","".join("@@"+f+"\n"for f in["001_schema.sql","002_shipping.sql","003_next.sql","004_depart.sql","005_recompile.sql","006_ledger.sql"]))
put("rollback.sql","""declare n number;begin select count(*)into n from(select OPERATION_ID from RRL_INTERWARE_ONWARD_DISPATCH group by OPERATION_ID having count(*)>1);if n>0 then raise_application_error(-20899,'CONSOLIDATED_HISTORY_REQUIRES_FORWARD_RECOVERY');end if;end;
/
@@000_before_rrl_stock_hu_ship_cmd.sql
@@000_before_rrl_stock_interware_next.sql
@@000_before_rrl_interware_depart_gate.sql
alter table RRL_INTERWARE_ONWARD_DISPATCH drop constraint RRL_IW_ONWARD_DISPATCH_PK;
alter table RRL_INTERWARE_ONWARD_DISPATCH add primary key(OPERATION_ID);
@@005_recompile.sql
""")
put("verify.sql","select NAME,TYPE,LINE,TEXT from USER_ERRORS where NAME in('RRL_STOCK_HU_SHIP_CMD','RRL_STOCK_INTERWARE_NEXT','RRL_INTERWARE_DEPART_GATE');\nselect OPERATION_ID,count(*)from RRL_INTERWARE_ONWARD_DISPATCH group by OPERATION_ID having count(*)>1;\n")
print(json.dumps(out))
