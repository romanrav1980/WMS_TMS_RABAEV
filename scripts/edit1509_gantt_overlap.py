from pathlib import Path
p=Path('api/wms_api_server/app/modules/transport/public.py');s=p.read_text(encoding='utf-8');s+='\nfrom .infrastructure.gantt_rows import gantt_rows, MAX_GANTT_ROWS\n';p.write_text(s,encoding='utf-8')
p=Path('api/wms_api_server/app/services/transport_service.py');s=p.read_text(encoding='utf-8');s=s.replace('normalize_transport_type as _normalize_transtype, available_sts_query','normalize_transport_type as _normalize_transtype, available_sts_query, gantt_rows, MAX_GANTT_ROWS')
a=s.index('        rows = self.gateway.fetch_all(',s.index('    def get_vehicles_gantt('));b=s.index('\n        result = []',a)
s=s[:a]+'''        rows = gantt_rows(self.gateway, gantt_date)
        if len(rows) > MAX_GANTT_ROWS:
            raise HTTPException(422, detail={"code": "GANTT_DAY_ROW_BOUND_EXCEEDED",
                                             "message": "Дневная диаграмма превышает предел 20000 операций; данные не обрезаны молча"})
'''+s[b:];p.write_text(s,encoding='utf-8')
