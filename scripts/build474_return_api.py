import json
from pathlib import Path
out={}
p=Path("api/wms_api_server/app/modules/delivery/api/store_return_routes.py");s=p.read_text(encoding="utf-8")
s=s.replace('    disposition: Literal["REUSE","SUPPLIER","DISPOSAL"]','    return_basis: Literal["ACCEPTED","REFUSED","DAMAGED"]="ACCEPTED"\n    disposition: Literal["REUSE","SUPPLIER","DISPOSAL"]')
s=s.replace('body.model_dump(exclude={"operation_id","line_no","unit_keys"})','body.model_dump(exclude={"operation_id","line_no","unit_keys","return_basis"})')
s=s.replace('**({"unit_keys":body.unit_keys} if body.unit_keys else {})','**({"unit_keys":body.unit_keys} if body.unit_keys else {}),**({"return_basis":body.return_basis}if body.return_basis!="ACCEPTED"else {})')
out[str(p)]=s
p=Path("api/wms_api_server/app/modules/delivery/infrastructure/store_returns.py");s=p.read_text(encoding="utf-8")
s=s.replace("to_char(l.ACCEPTED_BASE_QTY-nvl(a.APPROVED,0),'TM9','NLS_NUMERIC_CHARACTERS=''.,''') AVAILABLE_FOR_APPROVAL","""to_char(l.ACCEPTED_BASE_QTY-nvl(a.APPROVED,0),'TM9','NLS_NUMERIC_CHARACTERS=''.,''') AVAILABLE_FOR_APPROVAL,
                       to_char(l.REFUSED_BASE_QTY,'TM9','NLS_NUMERIC_CHARACTERS=''.,''') REFUSED_QUANTITY,
                       to_char(l.DAMAGED_BASE_QTY,'TM9','NLS_NUMERIC_CHARACTERS=''.,''') DAMAGED_QUANTITY,
                       to_char(l.REFUSED_BASE_QTY-nvl(a.REFUSED_APPROVED,0),'TM9','NLS_NUMERIC_CHARACTERS=''.,''') REFUSED_AVAILABLE,
                       to_char(l.DAMAGED_BASE_QTY-nvl(a.DAMAGED_APPROVED,0),'TM9','NLS_NUMERIC_CHARACTERS=''.,''') DAMAGED_AVAILABLE""")
s=s.replace("select LINE_NO,sum(BASE_QTY) APPROVED from RRL_STORE_RETURN_APPROVAL","""select LINE_NO,sum(case when RETURN_BASIS='ACCEPTED'then BASE_QTY else 0 end) APPROVED,
                       sum(case when RETURN_BASIS='REFUSED'then BASE_QTY else 0 end) REFUSED_APPROVED,
                       sum(case when RETURN_BASIS='DAMAGED'then BASE_QTY else 0 end) DAMAGED_APPROVED from RRL_STORE_RETURN_APPROVAL""")
s=s.replace("select a.OPERATION_ID,a.LINE_NO,a.DISPOSITION,","select a.OPERATION_ID,a.LINE_NO,a.RETURN_BASIS,a.DISPOSITION,")
start=s.index("            units=[]\n");end=s.index('            return {"units":units',start)
legacy=s[start:end];legacy=legacy.replace("            units=[]\n","").replace('dict(unit,line_no=line["line_no"],lot_uid=line["lot_uid"])','dict(unit,line_no=line["line_no"],lot_uid=line["lot_uid"],return_basis="ACCEPTED")')
legacy="\n".join("    "+line if line else line for line in legacy.splitlines())+"\n"
new="""            q.execute("select count(*)from RRL_STORE_RECEIPT_UNIT where OPERATION_ID=:receipt",receipt=receipt_id)
            modern=q.fetchone()[0]>0
            units=[]
            if modern:
                units=rows(\"\"\"select u.PHYSICAL_UNIT_KEY KEY,u.UNIT_ID,u.UID_PALLET ORIGIN_UID,
                    to_char(u.BASE_QTY,'TM9','NLS_NUMERIC_CHARACTERS=''.,''') QUANTITY,
                    u.BASE_UOM,u.UNIT_VERSION VERSION,l.LINE_NO,l.LOT_UID,fact.UNIT_DISPOSITION RETURN_BASIS
                    from RRL_STORE_RECEIPT_UNIT fact
                    join RRL_STORE_RECEIPT_FACT header on header.OPERATION_ID=fact.OPERATION_ID
                    join RRL_STOCK_OPERATION root on root.OPERATION_ID=header.OPERATION_ID and root.STATE='APPLIED'and root.COMMAND_TYPE='STORE_RECEIPT'
                    join RRL_WMS_RECEIPT_UNIT u on u.PHYSICAL_UNIT_KEY=fact.PHYSICAL_UNIT_KEY
                    and u.BASE_QTY=fact.BASE_QTY and u.BASE_UOM=fact.BASE_UOM and u.UNIT_VERSION=fact.SOURCE_UNIT_VERSION
                    join RRL_STORE_RECEIPT_LINE l on l.OPERATION_ID=fact.OPERATION_ID and l.LOT_UID=u.CURRENT_UID and l.BASE_UOM=u.BASE_UOM
                    where fact.OPERATION_ID=:receipt and fact.UNIT_DISPOSITION in('ACCEPTED','REFUSED','DAMAGED')
                    and u.CURRENT_CELL=json_value(header.COMPOSITION_JSON,'$.cell')
                    and u.STOCK_STATUS='ISSUED'and u.HARD_RESERVATION_ID is null
                    and not exists(select 1 from RRL_STORE_RETURN_UNIT assigned where assigned.RECEIPT_OPERATION_ID=fact.OPERATION_ID and assigned.PHYSICAL_UNIT_KEY=u.PHYSICAL_UNIT_KEY)
                    order by l.LINE_NO,fact.UNIT_DISPOSITION,u.PHYSICAL_UNIT_KEY fetch first 10001 rows only\"\"\",{"receipt":receipt_id})
                if len(units)>10000 or len({u["key"]for u in units})!=len(units):
                    raise StoreReceiptError("STORE_RETURN_UNIT_BOUND_OR_AMBIGUOUS_LINE","Разбейте состав или уточните исходную строку")
            else:
"""+legacy
s=s[:start]+new+s[end:];out[str(p)]=s
d=Path("db/migrations/2026-10-12_ni062_return_basis")
out[str(d/"007_compile.sql")]="\n".join("alter package "+n+" compile body;\n/\n"for n in ["RRL_STOCK_STORE_RETURN_SAP_CMD","RRL_STOCK_STORE_RETURN_TR_CMD","RRL_STOCK_STORE_RETURN_CUST_CMD","RRL_STOCK_STORE_RETURN_REC_CMD","RRL_STOCK_STORE_RETURN_PUT","RRL_STOCK_RETURN_REUSE","RRL_RETURN_REUSE_API","RRL_STOCK_POSTING_API"])
p=d/"apply.sql";s=p.read_text(encoding="utf-8");s=s.replace("alter package RRL_STOCK_POSTING_API compile body;\n/\n","@@007_compile.sql\n");out[str(p)]=s
print(json.dumps(out))
