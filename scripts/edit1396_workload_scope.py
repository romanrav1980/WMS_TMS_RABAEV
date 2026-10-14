from pathlib import Path
root=Path('api/wms_api_server/app/modules/resources')
p=root/'contracts_workload.py';s=p.read_text(encoding='utf-8').replace('from typing import Any,Protocol','from typing import Any,Protocol\nfrom datetime import datetime').replace('def configuration(self,ware: int,actor: str)', 'def configuration(self,ware: int,actor: str,site: str | None=None,start: datetime | None=None,finish: datetime | None=None)');p.write_text(s,encoding='utf-8')
p=root/'api/workload_config_routes.py';s=p.read_text(encoding='utf-8').replace('HTTPException,Path','HTTPException,Path,Query');old='def read_configuration(ware_id: int=Path(gt=0),user: AdminUser=Depends(require_permission("resource_shift_view")),service: WorkloadConfigPort=Depends(workload_config_service)) -> dict[str,Any]:\n    try:return service.configuration(ware_id,user.username)';new='''def read_configuration(ware_id: int=Path(gt=0),site_code: str | None=Query(None,min_length=1,max_length=50),
                       start_at: AwareDatetime | None=None,finish_at: AwareDatetime | None=None,
                       user: AdminUser=Depends(require_permission("resource_shift_view")),
                       service: WorkloadConfigPort=Depends(workload_config_service)) -> dict[str,Any]:
    if (start_at is None)!=(finish_at is None):
        raise HTTPException(422,"Укажите обе границы периода плановых выходов")
    if start_at is not None and (finish_at<=start_at or (finish_at-start_at).total_seconds()>31*86400):
        raise HTTPException(422,"Период должен быть положительным и не длиннее 31 дня")
    try:return service.configuration(ware_id,user.username,site_code,start_at,finish_at)''';assert old in s;s=s.replace(old,new);p.write_text(s,encoding='utf-8')
p=root/'infrastructure/workload_config.py';s=p.read_text(encoding='utf-8').replace('import json','import json\nfrom datetime import datetime,timezone');s=s.replace('def configuration(self,ware: int,actor: str)', 'def configuration(self,ware: int,actor: str,site: str | None=None,start: datetime | None=None,finish: datetime | None=None)');s=s.replace('''            cur.execute("""select n.WARE_ID''','''            norm_filter=" and n.SITE_CODE=:site" if site is not None else ""
            attendance_filter=" and a.SITE_CODE=:site" if site is not None else ""
            scoped={"ware":ware,**({"site":site} if site is not None else {})}
            attendance_params=dict(scoped)
            if start is not None and finish is not None:
                attendance_filter+=" and a.START_AT<:finish_at and a.FINISH_AT>:start_at"
                attendance_params.update(start_at=start.astimezone(timezone.utc),finish_at=finish.astimezone(timezone.utc))
            else:
                attendance_filter+=" and a.FINISH_AT>systimestamp-interval '1'day"
            cur.execute("""select n.WARE_ID''');s=s.replace('order by n.SITE_CODE,n.ARTICLE,n.BASE_UOM fetch first 501 rows only""",ware=ware)','"""+norm_filter+" order by n.SITE_CODE,n.ARTICLE,n.BASE_UOM fetch first 501 rows only",scoped)');s=s.replace("where a.WARE_ID=:ware and a.FINISH_AT>systimestamp-interval '1'day",'where a.WARE_ID=:ware');s=s.replace('order by a.START_AT,a.PLAN_OPERATION_ID fetch first 501 rows only""",ware=ware)','"""+attendance_filter+" order by a.START_AT,a.PLAN_OPERATION_ID fetch first 501 rows only",attendance_params)');s=s.replace('"Сузьте область просмотра настроек"','"Более 500 записей: выберите подсклад и период; список сотрудников ограничен складом"');s=s.replace('return {"warehouse_id":ware,"norms":norms','return {"warehouse_id":ware,"selection":{"site_code":site,"start_at":start.isoformat() if start else None,"finish_at":finish.isoformat() if finish else None},"norms":norms');p.write_text(s,encoding='utf-8')
p=Path('wiki-raw/wms_admin_ui_reference/resource-workload.js');s=p.read_text(encoding='utf-8');s=s.replace('''      const result = await request("/api/resources/workload/warehouses/" + ware());''','''      const query = new URLSearchParams();
      if (el("rwSite").value) query.set("site_code", el("rwSite").value);
      if (el("rwViewStart").value || el("rwViewFinish").value) {
        query.set("start_at", at("rwViewStart")); query.set("finish_at", at("rwViewFinish"));
      }
      const result = await request("/api/resources/workload/warehouses/" + ware() + "?" + query);''');s=s.replace('renderConfiguration(result); message("Настройки прочитаны.");','renderConfiguration(result); message("Настройки прочитаны: " + (result.selection?.site_code || "все подсклады") + (result.selection?.start_at ? " · выходы, пересекающие выбранный период." : " · текущие и будущие выходы."));');s=s.replace('el("rwResult").replaceChildren(); el("rwResult").replaceChildren();','el("rwResult").replaceChildren();');p.write_text(s,encoding='utf-8')