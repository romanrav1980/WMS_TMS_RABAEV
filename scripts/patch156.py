import json
from pathlib import Path
out={}
p=Path("api/wms_api_server/app/modules/inventory/infrastructure/slotting_candidates.py");s=p.read_text(encoding="utf-8")
s=s.replace("ar.ARTICUL=a.ARTICUL and ar.ACTIVE=1","ar.ARTICUL=a.ARTICUL")
s=s.replace("to_char(pf.MAX_WEIGHT,'TM9',q'[NLS_NUMERIC_CHARACTERS='.,']'),pf.PICK_ROUTE_ID,pf.PICK_ROUTE_CELL_ID","""to_char(pf.MAX_WEIGHT,'TM9',q'[NLS_NUMERIC_CHARACTERS='.,']'),
        case when pr.PICK_ROUTE_ID is not null and rc.PICK_ROUTE_CELL_ID is not null then pf.PICK_ROUTE_ID end,
        case when pr.PICK_ROUTE_ID is not null and rc.PICK_ROUTE_CELL_ID is not null then pf.PICK_ROUTE_CELL_ID end""")
s=s.replace("where pf.WARE_ID=:ware and pf.ACTIVE=1 and (pf.PICK_FACE_TYPE", """left join RRL_PICK_ROUTE pr on pr.PICK_ROUTE_ID=pf.PICK_ROUTE_ID and pr.WARE_ID=pf.WARE_ID and pr.ACTIVE=1 and pr.STATUS='PUBLISHED'
        left join RRL_PICK_ROUTE_CELL rc on rc.PICK_ROUTE_CELL_ID=pf.PICK_ROUTE_CELL_ID and rc.PICK_ROUTE_ID=pf.PICK_ROUTE_ID
         and rc.WARE_ID=pf.WARE_ID and rc.CELL_CODE=pf.CELL_CODE and rc.ACTIVE=1
        where pf.WARE_ID=:ware and pf.ACTIVE=1 and (pf.PICK_FACE_TYPE""")
out[str(p)]=s
p=Path("wiki-raw/wms_admin_ui_reference/slotting-demand.html");s=p.read_text(encoding="utf-8")
s=s.replace('<button id="sdRead">','''<label>Заявленная масса целой паллеты, брутто кг<input id="sdPalletWeight" inputmode="decimal"></label>
<label>Нормативы сравнения ячеек, по строке: ID; секунд отбора на базовую единицу; секунд пополнения на паллету; основание<textarea id="sdCosts" rows="5" placeholder="510; 0.8; 45; Замер маршрута смены"></textarea></label>
<p>Рекомендация использует не более одной дополнительной целой паллеты на ячейку. Нормативы — ваши допущения для сравнения; геометрия и утверждение проверяются отдельно.</p>
<button id="sdRead">''')
out[str(p)]=s
p=Path("wiki-raw/wms_admin_ui_reference/slotting-demand.js");s=p.read_text(encoding="utf-8")
s=s.replace('"sdForecast", "sdUnit"','"sdForecast", "sdUnit", "sdPalletWeight", "sdCosts"')
s=s.replace('      const base = auth()', '''      if (el("sdPalletWeight").value.trim()) body.declared_pallet_gross_weight_kg = el("sdPalletWeight").value.trim();
      const costLines = el("sdCosts").value.trim().split(/\\r?\\n/).filter(line => line.trim());
      body.recommendation_costs = costLines.map(line => {
        const parts = line.split(";").map(part => part.trim());
        if (parts.length !== 4 || !/^\\d+$/.test(parts[0]) || !Number.isSafeInteger(Number(parts[0]))) throw Error("Норматив: ID; секунды отбора на единицу; секунды пополнения; основание.");
        return {pick_face_id: Number(parts[0]), pick_seconds_per_base: parts[1],
          replenish_seconds_per_pallet: parts[2], basis: parts[3]};
      });
      const base = auth()''')
s=s.replace('      el("sdMessage").textContent = result.status', '''      const recommendation = result.range_recommendation;
      if (recommendation) {
        text("Рекомендация диапазона: " + recommendation.status + " · дополнительных целых паллет: " + (recommendation.required_additional_whole_pallets ?? "не определено"));
        text("Рекомендуемое число ячеек с сохранением старого диапазона: " + (recommendation.recommended_total_face_count ?? "нет полного расчёта"));
        if (recommendation.estimated_total_additional_seconds !== null && recommendation.estimated_total_additional_seconds !== undefined)
          text("Дополнительные затраты по заявленным нормативам: " + recommendation.estimated_total_additional_seconds + " секунд.");
        (recommendation.selected_faces || []).forEach(row => text("Предложено: " + row.cell + " · ячейка " + row.pick_face_id +
          " · целая паллета " + row.nominal_pallet_base_quantity + " " + unit + " · отбор " + row.estimated_pick_seconds +
          " сек · пополнение " + row.estimated_replenish_seconds + " сек"));
        (recommendation.candidates || []).forEach(row => text("Кандидат " + row.pick_face_id + " · " + row.cell + " · " +
          (row.refusal_reasons.length ? row.refusal_reasons.join(", ") : "номинально целая паллета помещается; нужна проверка геометрии и утверждение")));
        if ((recommendation.faces_without_declared_cost || []).length)
          text("Нужны нормативы для допустимых ячеек: " + recommendation.faces_without_declared_cost.join(", "));
        text("Слотирование и текущие задания сохранены. Рекомендация пока не утверждена.");
      }
      el("sdMessage").textContent = result.status''')
out[str(p)]=s
print(json.dumps(out))
