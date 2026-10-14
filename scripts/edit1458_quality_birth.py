from pathlib import Path
p=Path('db/migrations/2026-10-14_ni051_scoped_quality/002_reader.sql');s=p.read_text(encoding='utf-8').replace('batch_no varchar2(100);expiry date;produced date;', 'batch_no number;expiry date;produced date;birth_op varchar2(100);origin_uid varchar2(200);')
s=s.replace('select STOCK_COMPOSITION_VERSION,ARTICUL,PROD_BATCH_ID,EXPIRY_DATE,PRODUCED_DATE into epoch,article,batch_no,expiry,produced', 'select STOCK_COMPOSITION_VERSION,ARTICUL,PROD_BATCH_ID,EXPIRY_DATE,PRODUCED_DATE,CREATED_BY_STOCK_OP,STOCK_ORIGIN_UID into epoch,article,batch_no,expiry,produced,birth_op,origin_uid')
s=s.replace("or nvl(batch_no,chr(0))!=nvl(receipt.get_string('supplier_batch'),chr(0))", "or batch_no is not null or nvl(birth_op,chr(0))!=op or nvl(origin_uid,chr(0))!=uid")
s=s.replace("j.put('receipt_operation_id',op);", "j.put('supplier_batch',receipt.get_string('supplier_batch'));j.put('receipt_operation_id',op);")
p.write_text(s,encoding='utf-8')
