"""Thermal policy projection is read in the existing HU snapshot, never a sensor fact."""
from pathlib import Path
import sys,json
sys.path.insert(0,str(Path(__file__).resolve().parents[2]/'api/wms_api_server'))
from app.modules.inventory.infrastructure.hu_thermal_read import hu_thermal_admission


def test_current_projection_uses_native_nodes_and_location():
    calls=[]
    class Cursor:
        def callfunc(self,name,kind,args):
            calls.append((name,args));return json.dumps(dict(status='ADMISSIBLE',policy_only=True,observed_temperature_c=None))
    snapshot=dict(nodes=[dict(kind='STOCK',article='A')],warehouse=7,cell='C')
    result=hu_thermal_admission(Cursor(),snapshot)
    assert calls==[('RRL_HU_THERMAL_READ.admission_json',['[{"kind":"STOCK","article":"A"}]',7,'C',None])]
    assert result['policy_only']is True and result['observed_temperature_c']is None


def test_historical_projection_never_relabels_current_rules_as_departure_fact():
    result=hu_thermal_admission(None,dict(historical_composition=True))
    assert result['status']=='HISTORICAL_NOT_EVALUATED'and result['allowed']is None
    assert result['observed_temperature_c']is None
