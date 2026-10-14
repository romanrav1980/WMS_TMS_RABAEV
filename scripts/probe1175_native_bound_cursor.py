exec(open("scripts/ni063_slow_queries.py",encoding="utf-8").read().split("with oracledb.connect",1)[0])
d=json.loads(Path("tmp/context1168.json").read_text(encoding="utf-8"))
query="select /* CURRENT_LOAD_THERMAL_IN1173 */ distinct p.WARE_ID,r.ARTICUL,cfg.TEMP_MIN,cfg.TEMP_MAX from RRL_SBORKA_PALLETS p join RRL_SBORKA_PALLET_ROWS r on r.PALLET_UID=p.PALLET_UID left join RRL_RECEIPT_SKU_RULE cfg on cfg.WARE_ID=p.WARE_ID and cfg.ARTICUL=r.ARTICUL where p.ID in (:id0) order by p.WARE_ID,r.ARTICUL fetch first 1001 rows only"
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 c.call_timeout=5000;q=c.cursor();q.execute("set transaction read only");out=q.var(oracledb.DB_TYPE_CLOB)
 q.execute("""declare cur_no integer;rc sys_refcursor;ran integer;w number;a varchar2(32767);lo number;hi number;j json_object_t:=json_object_t();
 begin
  cur_no:=dbms_sql.open_cursor;dbms_sql.parse(cur_no,:query,dbms_sql.native);dbms_sql.bind_variable(cur_no,':id0',:source_id);
  ran:=dbms_sql.execute(cur_no);rc:=dbms_sql.to_refcursor(cur_no);cur_no:=null;
  fetch rc into w,a,lo,hi;
  if rc%notfound then raise_application_error(-20886,'OWN_THERMAL_SOURCE_MISSING');end if;
  j.put('warehouse_id',w);j.put('articul',a);j.put('temp_min_c',lo);j.put('temp_max_c',hi);close rc;:result:=j.to_clob;
 exception when others then
  if cur_no is not null then if dbms_sql.is_open(cur_no)then dbms_sql.close_cursor(cur_no);end if;end if;
  if rc%isopen then close rc;end if;raise;
 end;""",query=query,source_id=d["st_id"],result=out)
 value=out.getvalue();result=json.loads(value.read() if hasattr(value,"read")else value)
 assert result=={"warehouse_id":d["warehouse_id"],"articul":d["article"],"temp_min_c":2,"temp_max_c":6},result
 evidence=json.loads(Path("tmp/read1174_thermal_bounded_query.json").read_text(encoding="utf-8"))
 evidence["native_cursor_pipeline_validated"]=True;evidence["native_cursor_result"]=result
 Path("tmp/read1174_thermal_bounded_query.json").write_text(json.dumps(evidence,indent=2),encoding="utf-8")
 print("PASS1175 actual Oracle DBMS_SQL bind/execute/TO_REFCURSOR/fetch/close, current retained cold SKU2..6; read-only, no new goods/departure")
