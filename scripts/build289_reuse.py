exec(open("scripts/ni063_slow_queries.py",encoding="utf-8").read().split('with oracledb.connect',1)[0])
out={};base="db/migrations/2026-10-11_ni062_reuse_approval/"
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor()
 def ddl(kind,name):
  q.execute("select dbms_metadata.get_ddl(:kind,:object_name,user)from dual",kind=kind,object_name=name)
  return q.fetchone()[0].read().replace("\r\n","\n").replace("\r","\n").strip()+"\n/\n"
 spec=ddl("PACKAGE","RRL_STOCK_RETURN_REUSE");body=ddl("PACKAGE_BODY","RRL_STOCK_RETURN_REUSE");cmd=ddl("PACKAGE_BODY","RRL_STOCK_STORE_RETURN_CMD")
 out[base+"000_before_spec.sql"]=spec;out[base+"000_before_body.sql"]=body;out[base+"000_before_command.sql"]=cmd
 spec=spec.replace("package RRL_STOCK_STORE_RETURN_PUT)","package RRL_STOCK_STORE_RETURN_PUT,package RRL_STOCK_STORE_RETURN_CMD)")
 needle=" procedure describe_boxes("
 assert needle in spec
 spec=spec.replace(needle," procedure describe_source(p_lot varchar2,p_article varchar2,p_unit varchar2,p_qty number,p_proof out json_object_t);\n"+needle,1)
 helper="""
 procedure describe_source(p_lot varchar2,p_article varchar2,p_unit varchar2,p_qty number,p_proof out json_object_t)is
  lot RRL_PALLETS%rowtype;n number;batch varchar2(100);base varchar2(20);num number;den number;scale number;version number;box number;
 begin
  select *into lot from RRL_PALLETS where UID_PALLET=p_lot;
  if lot.ARTICUL!=p_article or lot.EXPIRY_DATE is null or trunc(lot.EXPIRY_DATE)<trunc(sysdate)then raise_application_error(-20886,'RETURN_REUSE_SOURCE_EXPIRY_ARTICLE_REQUIRED');end if;
  select count(*),min(SUPPLIER_BATCH)into n,batch from RRL_SAP_PALLET_RECEIPT where UID_PALLET=nvl(lot.STOCK_ORIGIN_UID,lot.UID_PALLET);
  if n!=1 or batch is null then raise_application_error(-20886,'RETURN_REUSE_ORIGINAL_VERIFIED_BATCH_GOOD_BOX_REQUIRED');end if;
  select BASE_UOM,NUMERATOR,DENOMINATOR,BASE_SCALE,POLICY_VERSION into base,num,den,scale,version from RRL_STOCK_UOM_CONVERSION
   where ARTICUL=p_article and INPUT_UOM='BOX'and POLICY_VERSION=(select max(POLICY_VERSION)from RRL_STOCK_UOM_CONVERSION where ARTICUL=p_article and INPUT_UOM='BOX');
  box:=RRL_STOCK_MATH.convert_exact('1',num,den,scale);
  if base!=p_unit or box<=0 or mod(p_qty,box)!=0 then raise_application_error(-20886,'RETURN_REUSE_FULL_BOX_BASE_QUANTITY_CONFLICT');end if;
  p_proof:=json_object_t();p_proof.put('supplier_batch',batch);p_proof.put('origin_uid',nvl(lot.STOCK_ORIGIN_UID,lot.UID_PALLET));
  p_proof.put('expiry_date',to_char(lot.EXPIRY_DATE,'YYYY-MM-DD'));p_proof.put('uom_policy_version',version);
  p_proof.put('box_count',RRL_STOCK_PLAN_HELPER.decimal_text(p_qty/box));p_proof.put('box_base_quantity',RRL_STOCK_PLAN_HELPER.decimal_text(box));
  p_proof.put('physical_completeness_verified',false);
 exception when no_data_found then raise_application_error(-20886,'RETURN_REUSE_CURRENT_SOURCE_BOX_UOM_REQUIRED');
 end;
"""
 needle=" procedure describe_boxes(";assert needle in body;body=body.replace(needle,helper+"\n"+needle,1)
 needle="source_cell varchar2(60);";assert needle in cmd;cmd=cmd.replace(needle,"source_cell varchar2(60);reuse_source json_object_t;",1)
 needle=" p_domain:=json_object_t();";assert needle in cmd
 cmd=cmd.replace(needle,needle+"""
 if v_destination='REUSE'then
  RRL_STOCK_RETURN_REUSE.describe_source(original.LOT_UID,original.ARTICLE,original.BASE_UOM,v_qty,reuse_source);
  p_domain.put('reuse_source',reuse_source);
 end;
""",1)
 assert "RRL_STOCK_STORE_RETURN_CMD)"in spec
 out[base+"001_reuse_helper.sql"]=spec+body;out[base+"002_command.sql"]=cmd
 out[base+"rollback.sql"]="@@000_before_command.sql\n@@000_before_spec.sql\n@@000_before_body.sql\n"
print(json.dumps(out,ensure_ascii=True))
