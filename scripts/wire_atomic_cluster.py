from pathlib import Path
p=Path("api/wms_api_server/app/services/transport_service.py")
s=p.read_text(encoding="utf-8-sig")
start=s.index('        # 2. Создать рейс',s.index('    def create_task_from_cluster('))
end=s.index('\n    def list_vehicles',start)
s=s[:start]+'''        from ..modules.transport.public import create_existing_cluster, TransportPlanError
        fields={key:value for key,value in {
            "transport":req.vehicle,"voditel_id":req.driver_id,"dock":req.dock,
        }.items() if value is not None}
        try:
            return create_existing_cluster(self.gateway,raion,req.stdate,
                _normalize_transtype(req.transtype),fields,
                [str(row["ST_NUMBER"]) for row in sts],user_id)
        except TransportPlanError as exc:
            raise HTTPException(exc.status,detail={"code":exc.code,"message":str(exc)}) from exc
''' +s[end:]
s=s.replace('''        Последовательность:
          1. list_available_sts → фильтр по raion
          2. RRL_TRASPORT_TASK_ADD  — создать рейс
          3. UPDATE TRANSPORT/VODITEL/DOCK (если переданы)
          4. RRL_TT_ADD_PALL × N   — назначить все СТ
          5. RRL_TT_REORDER_ADR    — оптимизировать порядок''','''        Существующий поиск СТ района; создание, реквизиты и назначение
        исполняются в одной транзакции с общим native capacity validator.''')
p.write_text(s,encoding="utf-8")
p=Path("api/wms_api_server/app/modules/transport/public.py")
s=p.read_text(encoding="utf-8-sig")+"\nfrom .infrastructure.cluster_creation import create_existing_cluster\n"
p.write_text(s,encoding="utf-8")
