source=__import__("pathlib").Path("scripts/source311_marked_case.py").read_text(encoding="utf-8-sig")
exec(source[:source.index('if Path("tmp/context311.json")')])
saved=json.loads(Path("tmp/source311_progress.json").read_text(encoding="utf-8-sig"));globals().update(saved);ware=saved["warehouse"];gtin=saved["barcode"]
if Path("tmp/context311.json").exists():raise SystemExit("Source311 complete; no repeat birth")
functions=source[source.index(" def meta("):source.index(' q.execute("select user,')]
a=source.index('  sscc_prefix="100"');continuation=" try:\n  import xml.etree.ElementTree as ET\n  receive='QR311'+tag;pick='QK311'+tag\n"+source[a:]
with oracledb.connect(user=cfg.oracle_user,password=cfg.oracle_password,dsn=cfg.oracle_dsn)as conn:
 q=conn.cursor()
 exec("\n".join(line[1:]if line.startswith(" ")else line for line in functions.splitlines()))
 import httpx
 from datetime import datetime,timedelta,timezone
 import xml.etree.ElementTree as ET
 admin_api=httpx.Client(auth=("admin","admin123"),timeout=35);base="http://127.0.0.1:8088"
 def api(method,path,body=None,status=200):
  r=admin_api.request(method,base+path,json=body);assert r.status_code==status,(r.status_code,r.text[:2200]);return r.json()
 idoc=ET.Element("ARTMAS10");doc=ET.SubElement(idoc,"IDOC");ctrl=ET.SubElement(doc,"EDI_DC40")
 def fields(node,values):
  for k,v in values.items():ET.SubElement(node,k).text=str(v)
 fields(ctrl,dict(MESTYP="ARTMAS",IDOCTYP="ARTMAS10",DOCNUM=str(4000000000000000+int(tag,16)),SNDPRN="OWN.QA.SAP",CREDAT="20261012",CRETIM="001500"))
 for segment,values in [("E1BPE1MATHEAD",{}),("E1BPE1MARART",dict(BASE_UOM="EA",EAN_UPC=gtin)),("E1BPE1MAKTRT",dict(LANGU_ISO="EN",MATL_DESC="Own311 SAP aggregation")),("E1BPE1MARMRT",dict(ALT_UNIT="EA",NUMERATOR="1",DENOMINATR="1",EAN_UPC=gtin))]:
  fields(ET.SubElement(doc,segment),dict(MATERIAL=article,**values))
 r=admin_api.post(base+"/api/integrations/sap/artmas",content=ET.tostring(idoc,encoding="utf-8"),headers={"Content-Type":"application/xml"});assert r.status_code==202,r.text
 continuation=continuation.replace('code=sscc)','code=lot)').replace('MessageId="IW311.SUPPLY:"','MessageId="IW311.SUPPLY2:"').replace('Revision=1','Revision=2');exec("\n".join(line[1:]if line.startswith(" ")else line for line in continuation.splitlines()))

