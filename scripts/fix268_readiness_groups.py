from pathlib import Path
import json
out={}
p=Path("api/wms_api_server/app/modules/fulfillment/infrastructure/preparation_readiness.py");s=p.read_text(encoding="utf-8")
s=s.replace('cur.execute(f"""select /* SOURCE_PICKING_READINESS268 */','cur.execute(f"""with demand as (select ARTICUL,sum(ORDER_QTY)ORDER_QTY,min(UNIT_CODE)UNIT_CODE,count(distinct UNIT_CODE)UNIT_COUNT\n            from RRL_CUSTOMER_ORDER_ROW where CUSTOMER_ORDER_ID=:order_id group by ARTICUL)\n            select /* SOURCE_PICKING_READINESS268 */')
s=s.replace('(select count(*)from RRL_ARTICULS z where z.ACTICUL=r.ARTICUL)','(select count(*)from RRL_ARTICULS z where z.ACTICUL=r.ARTICUL),r.UNIT_COUNT')
s=s.replace('from RRL_CUSTOMER_ORDER_ROW r left join','from demand r left join')
s=s.replace('where r.CUSTOMER_ORDER_ID=:order_id order by r.CUSTOMER_ORDER_ROW_ID','order by r.ARTICUL')
s=s.replace('rounded,count=row','rounded,count,unit_count=row')
s=s.replace('            if count!=1 or not found:','            if unit_count!=1:\n                errors.append("SOURCE_BASE_UNIT_AMBIGUOUS")\n            if count!=1 or not found:')
out[str(p)]=s
p=Path("wiki-raw/wms_admin_ui_reference/sap-store-admission.js");s=p.read_text(encoding="utf-8")
s=s.replace("  function cell(value)",'''  const preparationLabels={
    ALREADY_PREPARED_USE_SAVED_RESULT:'СТ уже подготовлена',
    SOURCE_NOT_ADMITTED:'Нет разрешения ERP',
    SOURCE_OPERATIONAL_STATE_FROZEN:'Исполнение уже началось',
    LEGACY_ADDRESS_MISSING:'Не задан адрес прежней СТ',
    CURRENT_CALENDAR_CLOSED:'Магазин закрыт для доставки в эту дату',
    CURRENT_CALENDAR_ZONE_CHANGED:'Изменился часовой пояс календаря',
    PICKING_DEADLINE_PASSED:'Истёк срок завершения отбора',
    LEGACY_ARTICLE_NOT_UNIQUE:'Нет однозначной карточки товара',
    SOURCE_PICKING_CELL_MISSING:'Не назначена ячейка отбора этого склада',
    PACKAGING_MASS_DIMENSIONS_REQUIRED:'Не заданы вложенность, масса или размеры коробки',
    LEGACY_ROUNDING_CHANGES_SOURCE_QUANTITY:'Округление коробок изменяет исходное количество',
    WHOLE_PACKAGING_LAYOUT_REQUIRED:'Для прежней СТ требуется целое число коробок',
    SOURCE_BASE_UNIT_AMBIGUOUS:'У строк товара разные базовые единицы',
    SOURCE_DEMAND_EMPTY:'Исходный заказ пуст'
  };
  function cell(value)''')
s=s.replace('...readiness.blockers,...readiness.lines.flatMap(line=>line.blockers.map(code=>line.articul+\': \'+code))','...readiness.blockers.map(code=>preparationLabels[code]||code),...readiness.lines.flatMap(line=>line.blockers.map(code=>line.articul+\': \'+(preparationLabels[code]||code)))')
out[str(p)]=s
print(json.dumps(out,ensure_ascii=True))
