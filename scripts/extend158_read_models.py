import json
from pathlib import Path
out={}
p=Path("api/wms_api_server/app/modules/inventory/infrastructure/slotting_candidates.py");s=p.read_text(encoding="utf-8").replace("import oracledb","import oracledb\nimport json")
s=s.replace("    result = recommend_range(scenario, layout[",'''    cur.execute("""select PICK_FACE_ARTICUL_ID,to_clob(json_object(* returning clob))
        from RRL_PICK_FACE_ARTICUL where ARTICUL=:article and ACTIVE=1
         and PICK_FACE_ID in(select ID from json_table(:faces,'$[*]'columns(ID number path '$')))
        order by PICK_FACE_ARTICUL_ID fetch first 101 rows only""",
        article=article, faces=json.dumps([row[0]for row in templates]))
    configuration = [{"pick_face_articul_id": identity,
        "native_configuration_json": raw.read() if hasattr(raw,"read") else raw} for identity,raw in cur.fetchall()]
    if len(configuration)>100:
        raise SlottingError("SLOTTING_TEMPLATE_CONFIGURATION_BOUND", "Сузьте область настроек")
    result = recommend_range(scenario, layout[''')
s=s.replace('"declared_costs": costs,','"template_configuration": configuration, "declared_costs": costs,')
out[str(p)]=s
p=Path("api/wms_api_server/app/modules/inventory/infrastructure/range_proposal.py");s=p.read_text(encoding="utf-8").replace("import json\n","")
s=s.replace('to_char(co.CREATED_AT at time zone \'UTC\',\'YYYY-MM-DD"T"HH24:MI:SS.FF6TZH:TZM\')', 'to_char(co.CREATED_AT at time zone \'UTC\',\'YYYY-MM-DD"T"HH24:MI:SS.FF6TZH:TZM\'),\n                ra.OPERATION_ID,ao.ACTOR,to_char(ao.CREATED_AT at time zone \'UTC\',\'YYYY-MM-DD"T"HH24:MI:SS.FF6TZH:TZM\')')
s=s.replace("left join RRL_PICK_RANGE_OPERATION co on co.OPERATION_ID=c.CANCEL_OPERATION_ID","left join RRL_PICK_RANGE_OPERATION co on co.OPERATION_ID=c.CANCEL_OPERATION_ID\n                left join RRL_PICK_RANGE_APPROVAL ra on ra.PROPOSAL_ID=p.PROPOSAL_ID\n                left join RRL_PICK_RANGE_OPERATION ao on ao.OPERATION_ID=ra.OPERATION_ID")
s=s.replace('            return {"proposal_id": proposal,', '''            cur.execute("""select m.PICK_FACE_ARTICUL_ID,m.ROLE_CODE,f.CELL_CODE,a.ACTIVE,s.MODE_CODE,s.APPROVAL_OPERATION_ID
                from RRL_PICK_RANGE_MEMBER m join RRL_PICK_FACE_ARTICUL a on a.PICK_FACE_ARTICUL_ID=m.PICK_FACE_ARTICUL_ID
                join RRL_PICK_FACE f on f.PICK_FACE_ID=a.PICK_FACE_ID
                left join RRL_PICK_RANGE_STATUS s on s.PICK_FACE_ARTICUL_ID=a.PICK_FACE_ARTICUL_ID
                where m.PROPOSAL_ID=:proposal and f.WARE_ID=:ware and a.ARTICUL=:article
                order by m.ROLE_CODE,m.PICK_FACE_ARTICUL_ID fetch first 201 rows only""",
                proposal=proposal,ware=ware,article=article)
            members=[dict(zip(["pick_face_articul_id","role","cell","mapping_active","current_mode","current_approval_operation_id"],item))
                     for item in cur.fetchall()]
            if len(members)>200:raise SlottingError("PICK_RANGE_MEMBER_BOUND","Сузьте область диапазона")
            return {"proposal_id": proposal,''')
s=s.replace('"status": "CANCELLED" if row[5] is not None else "DRAFT"', '"status": "APPROVED" if row[9] is not None else "CANCELLED" if row[5] is not None else "DRAFT"')
s=s.replace('"range_applied": False, "stock_changed": False}', '''"approval":None if row[9]is None else {"operation_id":row[9],"actor":row[10],"at":row[11]},
                    "range_members":members,"range_applied":row[9]is not None,"stock_changed":False,
                    "approved_range_superseded":row[9]is not None and any(m["role"]=="NEW" and
                        (m["current_mode"]!="ACTIVE"or m["current_approval_operation_id"]!=row[9])for m in members)}''')
out[str(p)]=s
print(json.dumps(out))
