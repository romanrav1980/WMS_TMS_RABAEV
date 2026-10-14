from pathlib import Path
p=Path('api/wms_api_server/app/routers/case_pick.py');s=p.read_text(encoding='utf-8');a=s.index('def create_case_pick_short(');b=s.index('@router.post',a);part=s[a:b]
anchor='    except CaseReadError as exc:\n        raise HTTPException(exc.status, {"code": exc.code, "message": str(exc)}) from exc\n'
part=part.replace(anchor,anchor+'''    except HTTPException as exc:
        detail = exc.detail if isinstance(exc.detail, dict) else {"message": str(exc.detail)}
        if exc.status_code == 422 or detail.get("code") == "CASE_SHORT_PICKED_FACT_MUST_BE_POSTED":
            raise HTTPException(exc.status_code, {**detail, "outcome_confirmed": True,
                "retry_same_operation_id": False, "offline_event_id": request.offline_event_id}) from exc
        raise
''');s=s[:a]+part+s[b:];p.write_text(s,encoding='utf-8')
