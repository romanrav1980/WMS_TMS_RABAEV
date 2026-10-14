from pathlib import Path
r=Path(__file__).resolve().parents[1]
p=r/"api/wms_api_server/app/modules/resources/infrastructure/case_assignment.py"
s=p.read_text(encoding="utf-8")
needle='        finally:\n            cursor.execute("begin RRL_STOCK_METADATA_TX.end_change;end;")'
replacement='''        except oracledb.DatabaseError as exc:
            code = getattr(exc.args[0], "code", 0)
            if 20800 <= code <= 20999:
                message = str(exc.args[0]).split("\\n", 1)[0]
                raise HTTPException(403 if code == 20882 else 409,
                    detail={"code": "CASE_ACTION_REJECTED", "message": message}) from exc
            raise
        finally:
            cursor.execute("begin RRL_STOCK_METADATA_TX.end_change;end;")'''
assert needle in s;s=s.replace(needle,replacement,1)
p.write_text(s,encoding="utf-8")
p=r/"scripts/ni033_case_http_close_flow.py"
s=p.read_text(encoding="utf-8")
s=s.replace('wave=None;case=None;plans=[];revision=None','wave=None;case=None;plans=[];revision=None;booking=None',1)
needle='  request(f"/tasks/{case}/claim",{});request(f"/tasks/{case}/start",{})'
replacement='''  q.execute("select PALLET_TYPE_ID from RRL_CASE_PICK_TASK where CASE_PICK_TASK_ID=:id",id=case);case_type=q.fetchone()[0]
  tare_base="http://127.0.0.1:8088/api/inventory/tare"
  availability=api.get(tare_base+f"/warehouses/{ware}/availability");assert availability.status_code==200,availability.text[:1200]
  current=next(row for row in availability.json()if row["pallet_type_id"]==case_type)
  observed=api.post(tare_base+"/count",json={"operation_id":"QA167.TARE.COUNT:"+str(case),"owner_ware_id":ware,"pallet_type_id":case_type,
      "condition":"GOOD","observed_quantity":"1","expected_version":current["balance_version"],
      "reason":"Own software fixture container observation, no hardware acceptance","decision_reference":"QA167:"+str(case)})
  assert observed.status_code==200,(observed.status_code,observed.text[:1300])
  booking="QA167.TARE.BOOK:"+str(case)
  booked=api.post(tare_base+"/book",json={"operation_id":booking,"place_kind":"CASE","place_id":str(case)})
  assert booked.status_code==200,(booked.status_code,booked.text[:1300])
  request(f"/tasks/{case}/claim",{});request(f"/tasks/{case}/start",{})'''
assert needle in s;s=s.replace(needle,replacement,1)
a=s.index('  q.execute("select r.UID_POLETA',s.index(' finally:'))
s=s[:a]+'''  if booking is not None:
   cancelled=api.post(tare_base+"/book-cancel",json={"operation_id":"QA167.TARE.CANCEL:"+str(case),"booking_operation_id":booking})
   assert cancelled.status_code==200,(cancelled.status_code,cancelled.text[:1300])
   availability=api.get(tare_base+f"/warehouses/{ware}/availability")
   current=next(row for row in availability.json()if row["pallet_type_id"]==case_type)
   observed=api.post(tare_base+"/count",json={"operation_id":"QA167.TARE.ZERO:"+str(case),"owner_ware_id":ware,"pallet_type_id":case_type,
       "condition":"GOOD","observed_quantity":"0","expected_version":current["balance_version"],
       "reason":"Retire owned empty software fixture container","decision_reference":"QA167.END:"+str(case)})
   assert observed.status_code==200,(observed.status_code,observed.text[:1300])
'''+s[a:]
p.write_text(s,encoding="utf-8")
