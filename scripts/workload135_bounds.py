from pathlib import Path
import json
out={}
p=Path('api/wms_api_server/app/modules/resources/domain/workload_intervals.py');s=p.read_text(encoding='utf-8-sig')
s=s.replace('result=[];begin=start','result=[];begin=start;unscheduled=[item["case_pick_line_id"]for item in work if item.get("window")is None]')
s=s.replace('None if blocked else','None if blocked or unscheduled else')
s=s.replace('"missing_norm_line_ids":blocked,','"missing_norm_line_ids":blocked,"unscheduled_line_ids":unscheduled,')
s+="""
def outside_view(start: datetime,end: datetime,work: list[dict[str,Any]]) -> list[dict[str,Any]]:
    result=[]
    with localcontext()as ctx:
        ctx.prec=60
        for item in work:
            window=item.get("window")
            if window is None:continue
            overlap=max(Decimal(0),hours(max(start,window[0]),min(end,window[1])))
            fraction=Decimal(1)-overlap/hours(*window)
            if fraction>0:
                value=Decimal(item["remaining_quantity"])*fraction
                result.append({"case_pick_line_id":item["case_pick_line_id"],"pick_wave_id":item["pick_wave_id"],
                    "article":item["article"],"base_uom":item["base_uom"],"estimated_quantity_outside":format(value,"f"),
                    "basis":"UNIFORM_WITHIN_EXPLICIT_WAVE_WINDOW"})
    return result
"""
out[str(p)]=s
p=Path('api/wms_api_server/app/modules/resources/infrastructure/workload_monitor.py');s=p.read_text(encoding='utf-8-sig')
s=s.replace('import interval_load','import interval_load,outside_view')
s=s.replace('"intervals":intervals,','"work_outside_view":outside_view(start,end,work),"intervals":intervals,')
s=s.replace("and(q.VALID_UNTIL is null or q.VALID_UNTIL>systimestamp))\n             and not exists", "and q.VALID_UNTIL is null)\n             and not exists")
out[str(p)]=s
p=Path('api/wms_api_server/app/modules/resources/infrastructure/workload_config.py');s=p.read_text(encoding='utf-8-sig').replace("and(q.VALID_UNTIL is null or q.VALID_UNTIL>systimestamp))","and q.VALID_UNTIL is null)")
out[str(p)]=s
p=Path('wiki-raw/wms_admin_ui_reference/resource-workload.js');s=p.read_text(encoding='utf-8-sig')
s=s.replace('      result.unscheduled_work.forEach', '      result.work_outside_view.forEach(row => text(el("rwResult"), "За пределами окна: волна " + row.pick_wave_id + " · " + row.article + " · около " + row.estimated_quantity_outside + " " + row.base_uom));\n      result.unscheduled_work.forEach')
out[str(p)]=s
print(json.dumps(out,ensure_ascii=True))
