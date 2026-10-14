import sys
from pathlib import Path
import oracledb
from stock_posting_environment import load_local_oracle_environment
load_local_oracle_environment();sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"api/wms_api_server"))
from app.config import get_settings
from app.modules.inventory.infrastructure.receiving import Receiving
from app.oracle_gateway import OracleGateway
from app.modules.inventory.api.receiving_routes import PalletReceipt
s=get_settings();tag="33bf3d9e";prefix=str(50000000000000000+int(tag,16));sscc=prefix+str((10-sum(int(n)*(3 if i%2==0 else 1)for i,n in enumerate(reversed(prefix)))%10)%10)
digits="0401234567890";gtin=digits+str((10-sum(int(n)*(3 if i%2==0 else 1)for i,n in enumerate(digits))%10)%10)
body={"operation_id":"WEIGHT180.RECEIVE:"+tag,"line_number":"1","sscc":sscc,"quantity":"9.8","supplier_batch":"WB:"+tag,"expiry_date":"2030-01-01","gross_weight":"12","capture_mode":"WEIGHTED_BOXES","policy_version":1,"weighted_boxes":[{"barcode":"(01)"+gtin+"(3103)009800(21)"+tag,"codes":[]}]}
print(Receiving(OracleGateway()).receive("44205c34cdde47df9a63b02a90581ef2",PalletReceipt(**body).model_dump(mode="json"),"admin"))
