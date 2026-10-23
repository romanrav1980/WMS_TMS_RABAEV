"""C-0160: build the NOT_APPLIED kit from the live sources dumped READ ONLY in ../src (minimal, asserted text edits)."""
import pathlib

S = pathlib.Path(__file__).resolve().parents[1] / "src"
D = pathlib.Path("C:/projects/TMS/db/migrations/2026-10-23_trade_pool_eligibility")
D.mkdir(parents=True, exist_ok=True)


def src(name, kind):
    return (S / f"{name}.{kind}.sql").read_text(encoding="utf-8").replace("\r\n", "\n")


def edit(text, pairs):
    for a, b in pairs:
        assert text.count(a) == 1, a[:90]
        text = text.replace(a, b)
    return text


def write(name, text):
    (D / name).write_text("create or replace " + text + "\n/\n", encoding="utf-8")


ctx_spec, ctx_body = src("RRL_TRADE_PICK_CONTEXT", "PACKAGE"), src("RRL_TRADE_PICK_CONTEXT", "PACKAGE_BODY")
read_body, cmd_body = src("RRL_STOCK_POOL_READ", "PACKAGE_BODY"), src("RRL_STOCK_POOL_CMD", "PACKAGE_BODY")
for name, text in (("before_ctx_spec.sql", ctx_spec), ("before_ctx_body.sql", ctx_body), ("before_pool_read.sql", read_body), ("before_pool_cmd.sql", cmd_body)):
    write(name, text)

# 1. Pick context: the same line rules for the pool, without the reader's own owner access (the pool snapshot must not depend on who reads).
write("001_ctx_spec.sql", edit(ctx_spec, [
    ("package RRL_STOCK_CASE_PICK_CMD)as", "package RRL_STOCK_CASE_PICK_CMD,package RRL_STOCK_POOL_READ)as"),
    (" function reason(p_uid varchar2,p_cell varchar2,p_ware number,p_purpose varchar2 default 'ALLOCATE')return varchar2;\nend;",
     " function reason(p_uid varchar2,p_cell varchar2,p_ware number,p_purpose varchar2 default 'ALLOCATE')return varchar2;\n"
     " -- C-0160: whether one order row may be served from this source by the trade rules (binding, SKU/MRC, OSG, owner, buyout, whole box),\n"
     " -- without the reader's owner access: the common pool snapshot is the same for every reader; its command checks access itself.\n"
     " -- The caller's current line context is kept.\n"
     " function compatible(p_row number,p_uid varchar2,p_cell varchar2,p_ware number)return varchar2;\nend;")]))
write("002_ctx_body.sql", edit(ctx_body, [
    (" function reason(p_uid varchar2,p_cell varchar2,p_ware number,p_purpose varchar2 default 'ALLOCATE')return varchar2 is\n",
     " function check_source(p_uid varchar2,p_cell varchar2,p_ware number,p_purpose varchar2,p_access boolean)return varchar2 is\n"),
    ("  if RRL_TRADE_STOCK_GUARD.owner_allowed(g_actor,p_ware,v_owner,g_write)<>1 then return 'TRADE_OWNER_ACCESS_DENIED';end if;",
     "  if p_access and RRL_TRADE_STOCK_GUARD.owner_allowed(g_actor,p_ware,v_owner,g_write)<>1 then return 'TRADE_OWNER_ACCESS_DENIED';end if;"),
    ("  return null;\n end;\nend;",
     "  return null;\n end;\n"
     " function reason(p_uid varchar2,p_cell varchar2,p_ware number,p_purpose varchar2 default 'ALLOCATE')return varchar2 is\n"
     " begin return check_source(p_uid,p_cell,p_ware,p_purpose,true);end;\n"
     " function compatible(p_row number,p_uid varchar2,p_cell varchar2,p_ware number)return varchar2 is\n"
     "  s_line RRL_TRADE_ORDER_LINE%rowtype:=g_line;s_write number:=g_write;s_ware number:=g_ware;s_actor varchar2(50):=g_actor;\n"
     "  s_tx varchar2(100):=g_tx;s_valid boolean:=g_valid;v varchar2(100);\n"
     "  procedure restore is begin g_line:=s_line;g_write:=s_write;g_ware:=s_ware;g_actor:=s_actor;g_tx:=s_tx;g_valid:=s_valid;end;\n"
     " begin\n"
     "  enter_line(p_row,null);v:=check_source(p_uid,p_cell,p_ware,'ALLOCATE',false);restore;return v;\n"
     " exception when others then restore;raise;\n"
     " end;\nend;")]))

# 2. Pool snapshot: trade sources become classes; every open row lists its compatible classes or a concrete reason.
write("003_pool_read.sql", edit(read_body, [
    ("  n number;num number;den number;scale number;qty number;hard_qty number;picked_qty number;picked_hard number;conversion number;note varchar2(100);tp number;held number;\n",
     "  n number;num number;den number;scale number;qty number;hard_qty number;picked_qty number;picked_hard number;conversion number;note varchar2(100);tp number;held number;\n"
     "  -- C-0160 trade site: physical classes (owner|SKU|MRC|expiry; a pallet is homogeneous by the trade guard) and their eligible quantity.\n"
     "  type num_map is table of number index by varchar2(400);type txt_map is table of varchar2(200) index by varchar2(400);\n"
     "  trade number:=0;cfree num_map;cuid txt_map;ccell txt_map;cowner txt_map;ckey varchar2(400);cown varchar2(100);k varchar2(400);\n"
     "  comp json_array_t;why varchar2(100);r varchar2(100);pairs number:=0;classes json_array_t:=json_array_t();\n"),
    ("  if enabled=1 and n>0 then raise_application_error(-20886,'POOL_LEGACY_SOFT_REQUIRES_RECONCILIATION');end if;\n",
     "  if enabled=1 and n>0 then raise_application_error(-20886,'POOL_LEGACY_SOFT_REQUIRES_RECONCILIATION');end if;\n"
     "  select count(*)into trade from RRL_TRADE_SITE where WARE_ID=p_ware and ENABLED=1;\n"),
    ("   eligible:=0;note:=RRL_STOCK_ELIGIBILITY.reason(s.UID_POLETA,s.CELL,p_ware,0,null,null,'ALLOCATE',null,p_article);\n",
     "   eligible:=0;note:=RRL_STOCK_ELIGIBILITY.reason(s.UID_POLETA,s.CELL,p_ware,0,null,null,'ALLOCATE',null,p_article);\n"
     "   -- The trade guard answers this only after every source check passed: what remains is the per-row check below.\n"
     "   if trade=1 and note='TRADE_ORDER_BINDING_REQUIRED'then note:=null;end if;\n"),
    ("   x.put('stock_version',s.STOCK_VERSION);x.put('free',RRL_STOCK_PLAN_HELPER.decimal_text(eligible));x.put('reason',note);stocks.append(x);\n",
     "   x.put('stock_version',s.STOCK_VERSION);x.put('free',RRL_STOCK_PLAN_HELPER.decimal_text(eligible));x.put('reason',note);\n"
     "   if trade=1 and eligible>0 then\n"
     "    select min(a.OWNER_ID)||'|'||min(a.SKU_ID)||'|'||RRL_STOCK_PLAN_HELPER.decimal_text(min(a.MRC))||'|'||to_char(min(a.EXPIRY_DATE),'YYYY-MM-DD'),min(a.OWNER_ID)\n"
     "     into ckey,cown from RRL_TRADE_STOCK_ATTR a join RRL_WMS_RECEIPT_UNIT u on u.PHYSICAL_UNIT_KEY=a.PHYSICAL_UNIT_KEY\n"
     "     where u.CURRENT_UID=s.UID_POLETA and u.CURRENT_CELL=s.CELL and u.STOCK_STATUS<>'ISSUED';\n"
     "    if not cfree.exists(ckey)then cfree(ckey):=0;cuid(ckey):=s.UID_POLETA;ccell(ckey):=s.CELL;cowner(ckey):=cown;end if;\n"
     "    cfree(ckey):=cfree(ckey)+eligible;x.put('class',ckey);\n"
     "   end if;\n"
     "   stocks.append(x);\n"),
    ("    x.put('quantity',RRL_STOCK_PLAN_HELPER.decimal_text(greatest(0,qty-held)));\n   end if;\n",
     "    x.put('quantity',RRL_STOCK_PLAN_HELPER.decimal_text(greatest(0,qty-held)));\n   end if;\n"
     "   -- C-0160: a trade row may take only classes its own terms accept; otherwise the concrete reason, never a silent zero.\n"
     "   if trade=1 and enabled=1 and x.get_string('quantity')<>'0'then\n"
     "    comp:=json_array_t();why:=null;k:=cfree.first;\n"
     "    while k is not null loop\n"
     "     pairs:=pairs+1;if pairs>2000 then raise_application_error(-20881,'POOL_TRADE_MATRIX_BOUND_2000');end if;\n"
     "     r:=RRL_TRADE_PICK_CONTEXT.compatible(o.CUSTOMER_ORDER_ROW_ID,cuid(k),ccell(k),p_ware);\n"
     "     if r is null then comp.append(k);elsif why is null then why:=r;elsif why<>r then why:='POOL_TRADE_NO_COMPATIBLE_SOURCE';end if;\n"
     "     k:=cfree.next(k);\n"
     "    end loop;\n"
     "    x.put('classes',comp);\n"
     "    if comp.get_size=0 then x.put('pool_reason',nvl(why,'POOL_TRADE_NO_ELIGIBLE_SOURCE'));end if;\n"
     "   end if;\n"),
    ("  j.put('warehouse',p_ware);j.put('article',p_article);j.put('from_stock',enabled);j.put('policy_version',ver);\n",
     "  k:=cfree.first;\n"
     "  while k is not null loop x:=json_object_t();x.put('key',k);x.put('owner',cowner(k));x.put('free',RRL_STOCK_PLAN_HELPER.decimal_text(cfree(k)));classes.append(x);k:=cfree.next(k);end loop;\n"
     "  if trade=1 then j.put('trade',1);j.put('classes',classes);end if;  -- non-trade snapshots stay byte-identical\n"
     "  j.put('warehouse',p_ware);j.put('article',p_article);j.put('from_stock',enabled);j.put('policy_version',ver);\n"),
]))

# 3. Pool command: a trade plan names its source classes per row; compile proves them, execute checks the actor's owner rights.
write("004_pool_cmd.sql", edit(cmd_body, [
    (" procedure compile_command(p_request clob,p_operation varchar2,p_hints clob,p_policies out clob,p_resources out clob,p_domain out clob) is\n",
     " -- C-0160: trade plan proof. Every allocated row names quantities per physical class: each class is one this row accepts, every share is\n"
     " -- a whole pick step, the shares make the row's allocation, and no class is promised beyond its eligible quantity.\n"
     " procedure prove_trade(s json_object_t,h json_object_t,step number)is\n"
     "  type num_map is table of number index by varchar2(400);used num_map;free num_map;\n"
     "  a json_array_t:=s.get_array('orders');cls json_array_t:=s.get_array('classes');x json_object_t;src json_object_t;ls json_object_t;comp json_array_t;\n"
     "  keys json_key_list;lid varchar2(40);qty number;q number;total number;ok boolean;key_value varchar2(400);\n"
     " begin\n"
     "  if not h.has('sources')then raise_application_error(-20881,'POOL_TRADE_SOURCES_REQUIRED');end if;\n"
     "  src:=h.get_object('sources');\n"
     "  for i in 0..cls.get_size-1 loop x:=treat(cls.get(i) as json_object_t);free(x.get_string('key')):=nonnegative(x.get_string('free'));used(x.get_string('key')):=0;end loop;\n"
     "  for i in 0..a.get_size-1 loop\n"
     "   x:=treat(a.get(i) as json_object_t);lid:=RRL_STOCK_PLAN_HELPER.decimal_text(x.get_number('line_id'));\n"
     "   qty:=nonnegative(h.get_object('allocations').get_string(lid));total:=0;\n"
     "   if qty>0 and x.has('pool_reason')then raise_application_error(-20881,'POOL_TRADE_LINE_NOT_ALLOCATABLE');end if;\n"
     "   if src.has(lid)then\n"
     "    ls:=src.get_object(lid);keys:=ls.get_keys;comp:=x.get_array('classes');\n"
     "    for k in 1..keys.count loop\n"
     "     key_value:=keys(k);q:=nonnegative(ls.get_string(key_value));ok:=false;\n"
     "     if comp is not null then for c in 0..comp.get_size-1 loop if comp.get_string(c)=key_value then ok:=true;exit;end if;end loop;end if;\n"
     "     if q>0 and(not ok or not used.exists(key_value))then raise_application_error(-20881,'POOL_TRADE_SOURCE_INCOMPATIBLE');end if;\n"
     "     if mod(q,step)!=0 then raise_application_error(-20881,'POOL_ALLOCATION_INVALID');end if;\n"
     "     if q>0 then used(key_value):=used(key_value)+q;end if;total:=total+q;\n"
     "    end loop;\n"
     "   end if;\n"
     "   if total!=qty then raise_application_error(-20881,'POOL_TRADE_SOURCE_SPLIT_INVALID');end if;\n"
     "  end loop;\n"
     "  key_value:=used.first;\n"
     "  while key_value is not null loop\n"
     "   if used(key_value)>free(key_value)then raise_application_error(-20881,'POOL_TRADE_CLASS_OVERALLOCATED');end if;key_value:=used.next(key_value);\n"
     "  end loop;\n"
     " end;\n"
     " procedure compile_command(p_request clob,p_operation varchar2,p_hints clob,p_policies out clob,p_resources out clob,p_domain out clob) is\n"),
    ("  if total>available then raise_application_error(-20881,'POOL_OVERALLOCATED');end if;\n",
     "  if total>available then raise_application_error(-20881,'POOL_OVERALLOCATED');end if;\n"
     "  if nvl(s.get_number('trade'),0)=1 then prove_trade(s,h,step);v.put('sources',h.get_object('sources'));end if;\n"),
    ("  if not same_snapshot(raw_snapshot,RRL_STOCK_POOL_READ.snapshot_json(ware,article)) then raise_application_error(-20890,'CLOSURE_CHANGED: locked pool snapshot');end if;\n",
     "  if not same_snapshot(raw_snapshot,RRL_STOCK_POOL_READ.snapshot_json(ware,article)) then raise_application_error(-20890,'CLOSURE_CHANGED: locked pool snapshot');end if;\n"
     "  -- C-0160: today's operate right on the owner of every class this trade plan promises; the snapshot itself is reader-independent.\n"
     "  if nvl(s.get_number('trade'),0)=1 then\n"
     "   declare cls json_array_t:=s.get_array('classes');src json_object_t:=v.get_object('sources');ls json_object_t;keys json_key_list;c json_object_t;\n"
     "   begin\n"
     "    for i in 0..cls.get_size-1 loop\n"
     "     c:=treat(cls.get(i) as json_object_t);\n"
     "     keys:=src.get_keys;\n"
     "     for k in 1..keys.count loop\n"
     "      ls:=src.get_object(keys(k));\n"
     "      if ls.has(c.get_string('key'))and nonnegative(ls.get_string(c.get_string('key')))>0 then\n"
     "       RRL_TRADE_STOCK_GUARD.assert_owner(p_actor,ware,c.get_string('owner'),1);exit;\n"
     "      end if;\n"
     "     end loop;\n"
     "    end loop;\n"
     "   end;\n"
     "  end if;\n"),
]))
print("kit written to", D)
