import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"api/wms_api_server"))
from app.modules.integrations.domain.article_logistics import box_logistics

def records(**data):
 return [{"segment":"E1BPE1MARMRT","fields":{"ALT_UNIT":"BOX",**data}}]
out=box_logistics(records(GROSS_WT="10000",UNIT_OF_WT="G",UNIT_OF_WT_ISO="GRM",LENGTH="40",WIDTH="30",HEIGHT="20",UNIT_DIM="CM",UNIT_DIM_ISO="CMT"))
assert out=={"BRUTTO_WEIGHT_OF_KOR":10,"DIMKOR_X":400,"DIMKOR_Y":300,"DIMKOR_Z":200}
assert box_logistics(records())=={}
sparse=records(GROSS_WT="10",UNIT_OF_WT="KG",LENGTH="400",WIDTH="300",HEIGHT="200",UNIT_DIM="MM")
sparse.append({"segment":"E1BPE1MARMRTX","fields":{"ALT_UNIT":"BOX","LENGTH":"X"}})
assert box_logistics(sparse)=={"DIMKOR_X":400}
for data in [dict(GROSS_WT="1",UNIT_OF_WT="LB"),dict(GROSS_WT="1",UNIT_OF_WT="KG",UNIT_OF_WT_ISO="GRM"),dict(LENGTH="0",UNIT_DIM="MM"),dict(LENGTH="10")]:
 try:box_logistics(records(**data))
 except ValueError:pass
 else:raise AssertionError(data)
print("PASS271 exact cm-to-mm/g-to-kg/ISO alias agreement/sparse dimension X/missing unchanged/unknown-contradictory-zero-unitless rejected")
