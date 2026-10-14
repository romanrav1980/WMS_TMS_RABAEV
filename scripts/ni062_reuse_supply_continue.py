import sys,xml.etree.ElementTree as ET
from pathlib import Path
from stock_posting_environment import load_local_oracle_environment
load_local_oracle_environment()
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"api/wms_api_server"))
from app.oracle_gateway import OracleGateway
from app.modules.integrations.infrastructure.supply_orders import SupplyOrders
tag="cdbf4c0962";ware=100000+int(tag[:6],16);article="REUSE.QA:"+tag
root=ET.Element("WarehouseSupplyOrder",version="1")
for name,value in {"Sender":"OWN.QA.SAP","MessageId":"REUSE.SUPPLY:"+tag,"OrderNumber":"REUSE:"+tag,"Revision":"1","WarehouseId":ware,"ReceiveCell":"QIN"+tag,"Supplier":"Own software fixture"}.items():ET.SubElement(root,name).text=str(value)
line=ET.SubElement(ET.SubElement(root,"Lines"),"Line")
ET.SubElement(line,"LineNumber").text="1";ET.SubElement(line,"Material").text=article;ET.SubElement(line,"Quantity",unit="EA").text="24"
print(SupplyOrders(OracleGateway()).receive(ET.tostring(root,encoding="utf-8"),"admin"))
