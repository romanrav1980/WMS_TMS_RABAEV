from pathlib import Path
p=Path('api/wms_api_server/app/modules/finance/infrastructure/reconciliation_stock_documents.py');s=p.read_text(encoding='utf-8').replace('"available":True,"document_kind":"STOCK_ROW"','"available":True,"metric":key,"document_kind":"STOCK_ROW"');p.write_text(s,encoding='utf-8')
p=Path('wiki-raw/wms_admin_ui_reference/day-reconciliation-documents.js');s=p.read_text(encoding='utf-8').replace("'. Остальные конфликтные строки требуют отдельной выборки по складу.'", "'. Продолжение доступно в реестре конфликтов ниже.'");s=s.replace("  card.dataset.search+=", """  if(documents.document_kind==='STOCK_ROW'&&['stock_quantity_invariants','physical_unit_composition'].includes(documents.metric)){
   const link=node('a','Открыть постраничный реестр конфликтов');
   link.href='day-reconciliation.html?warehouse_id='+encodeURIComponent(warehouse)+'&stock_metric='+encodeURIComponent(documents.metric)+'#stockConflicts';
   link.title='Читать текущие конфликты по50 строк; никаких исправлений запаса';details.append(link);
  }
  card.dataset.search+=""");p.write_text(s,encoding='utf-8')
p=Path('wiki-raw/wms_admin_ui_reference/day-reconciliation.html');s=p.read_text(encoding='utf-8').replace('<script src="day-review.js">','<script src="stock-conflicts.js"></script><script src="day-review.js">');p.write_text(s,encoding='utf-8')
