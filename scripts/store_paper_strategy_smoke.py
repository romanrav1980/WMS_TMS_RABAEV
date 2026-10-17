"""Verify the existing committed DEV paper receipt and exact replay; never create a new receipt."""
import json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'api/wms_api_server'),str(ROOT/'scripts')]
from stock_posting_environment import load_local_oracle_environment
load_local_oracle_environment()
from app.oracle_gateway import OracleGateway
from app.modules.inventory.public import StockCommand,StockPosting,StockPostingError

def main():
 g=OracleGateway();operation='PAPER.ROLLBACK:41005408317040d0b433353978c38d9a:2';checks=[]
 row=g.fetch_all('select CANONICAL_REQUEST,RESULT_JSON,STATE from RRL_STOCK_OPERATION where OPERATION_ID=:op',{'op':operation})[0]
 decode=lambda value:value if isinstance(value,dict)else json.loads(value)
 request=decode(row['canonical_request']);original=decode(row['result_json'])
 assert row['state']=='APPLIED'and original['receipt_mode']=='PAPER_COUNT'and original['status']=='ACCEPTED'
 assert original['warehouse_stock_consumed_again']is False
 checks.append('existing_committed_dev_paper_receipt_strategy_and_explicit_counts')
 def command(metadata):return StockCommand(operation_id=operation,command_type=request['command_type'],actor=request['actor'],source=request['source'],lines=(),units=tuple(request['units']),metadata=metadata)
 posting=StockPosting();a=posting.post(command(request['metadata']));b=posting.post(command(request['metadata']))
 assert a==b==original;checks.append('unchanged_operation_replays_same_original_receipt_after_policy_restored')
 changed=dict(request['metadata'],paper_reference='DIFFERENT.PAPER.DOCUMENT')
 try:posting.post(command(changed))
 except StockPostingError as error:assert error.rule_reason and 'OPERATION_CONFLICT'in error.rule_reason,(error.code,error.oracle_code,error.rule_reason)
 else:raise AssertionError('Changed payload accepted under same key')
 checks.append('changed_document_same_operation_conflict')
 count=g.fetch_all('select count(*) N from RRL_STORE_RECEIPT_FACT where LOAD_OPERATION_ID=:load',{'load':request['source']['load_operation_id']})[0]['n']
 assert count==1
 policy=g.fetch_all('select RECEIPT_MODE from RRL_STORE_RECEIPT_POLICY where STORE_ADDR=:a',{'a':request['source']['store_address']})[0]['receipt_mode'];assert policy=='BARCODE'
 checks.append('single_receipt_no_second_acceptance_and_dev_policy_restored')
 result=dict(status='PASS',checks=checks,receipt_state='EXISTING_COMMITTED_DEV_FIXTURE',original_operation_id=operation,receipt_count=count,new_receipts=0,warehouse_stock_consumed_again=False,dev_policy_mode_restored=True)
 target=ROOT/'reports/retailcase/2026-10-15/store-app';target.mkdir(exist_ok=True)
 (target/'paper-native.json').write_text(json.dumps(result,indent=2),encoding='utf-8');print(json.dumps(result))
if __name__=='__main__':main()
