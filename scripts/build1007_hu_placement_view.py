from pathlib import Path
import json
read=lambda p:Path(p).read_text(encoding="utf-8");files={}
p="api/wms_api_server/app/modules/inventory/infrastructure/warehouse_hu.py";v=read(p)
v=v.replace('from ..domain.historical_hu import departure_subtree','from ..domain.historical_hu import departure_subtree\nfrom .hu_placement_read import recorded_placement',1)
needle='            assert_hu_view(cur, actor, int(data["warehouse"]))';assert v.count(needle)==1
v=v.replace(needle,needle+'\n            data["placement"] = recorded_placement(cur, data)',1);files[p]=v
p="wiki-raw/wms_admin_ui_reference/warehouse-hus.js";v=read(p)
needle='    el("huSummary").textContent=';assert v.count(needle)==1
pos=v.index(needle);end=v.index('\n  }',pos)
v=v[:end]+'''
    const placement=el("huPlacement");placement.replaceChildren();placement.hidden=!data.placement;
    if(data.placement){
      const p=data.placement,label=document.createElement("strong"),note=document.createElement("span"),link=document.createElement("a");
      label.textContent="Физический слот: "+p.slot_code;
      note.textContent="Замер при размещении: "+(p.gross_weight_kg??"—")+" кг, "+(p.bounding_volume_m3??"—")+" м³; версия "+(p.content_version??"—")+
        (p.version_matches?"":" · версия места изменилась")+(p.slot_active?"":" · слот отключён")+". Новая операция повторно проверит состав и вместимость.";
      link.textContent="Задание размещения #"+p.task_id+" →";link.href="warehouse-tasks.html?task_id="+encodeURIComponent(p.task_id)+"#warehouseTaskDetail";
      placement.append(label,note,link);
    }'''+v[end:]
v=v.replace('    }catch(e){status(e.message);}\n  }\n  function reviewed()','    }catch(e){if(id===generation&&key()===scope)status(e.message);}\n  }\n  function reviewed()',1)
files[p]=v
p="wiki-raw/wms_admin_ui_reference/warehouse-hus.html";files[p]=read(p).replace('<div id="huSummary"></div>','<div id="huSummary"></div><div id="huPlacement" hidden></div>',1).replace('warehouse-hus.js?v=20261013-1004','warehouse-hus.js?v=20261013-1007').replace('warehouse-hus.css?v=20261013-998','warehouse-hus.css?v=20261013-1007')
p="wiki-raw/wms_admin_ui_reference/warehouse-hus.css";files[p]=read(p)+'\n.hu-page #huPlacement:not([hidden]){display:grid;gap:8px;padding:14px 16px;border-left:4px solid #5596eb;background:#f2f7ff;border-radius:8px;margin-bottom:16px}.hu-page #huPlacement span{font-size:13px;color:#66788e;line-height:1.5}.hu-page #huPlacement a{font-size:13px;font-weight:600}\n'
print(json.dumps(files,ensure_ascii=True))
