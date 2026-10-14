"""All physical adapters deny PREPARED instead of selecting a second executor."""
import sys
from pathlib import Path
from types import SimpleNamespace
sys.path.insert(0,str(Path(__file__).resolve().parents[2]/"api/wms_api_server"))
import pytest
from app.modules.inventory.contracts_stock import StockPostingError
from app.modules.inventory.infrastructure.release_boundary import require_active_release
from app.modules.inventory.infrastructure.case_pick_commands import post_case_pick
from app.modules.inventory.infrastructure.case_short_commands import post_short_approval
from app.modules.inventory.infrastructure.document_reservation_commands import release_document_reservations
from app.modules.inventory.infrastructure.reservation_commands import post_reservation
from app.modules.inventory.infrastructure.wave_commands import reserve_wave_sources
from app.modules.inventory.infrastructure.mes_commands import apply_mes_movements
from app.modules.inventory.infrastructure.mes_release_commands import release_supply
from app.modules.inventory.infrastructure.mes_supply_commands import calculate_supply
from app.modules.inventory.infrastructure.mes_task_commands import post_mes_task
from app.modules.inventory.infrastructure.terminal_quality_commands import post_terminal_quality

class Inactive:
 def __init__(self,state="PREPARED"):self.state=state
 def fetch_all(self,sql,*args):
  assert sql=="select STATE from RRL_STOCK_RELEASE where RELEASE_ID=1"
  return []if self.state is None else[{"state":self.state}]
 def transaction(self,*args):raise AssertionError("No effect preparation or transaction")
 def execute(self,*args):raise AssertionError("No legacy write")

@pytest.mark.parametrize("state",["PREPARED","CUTOVER",None])
def test_inactive_kernel_contract(state):
 with pytest.raises(StockPostingError)as caught:require_active_release(Inactive(state),"BOUND148")
 assert caught.value.code=="STOCK_RELEASE_NOT_ACTIVE"and caught.value.operation_id=="BOUND148"

@pytest.mark.parametrize("call",[
 lambda g,r:post_case_pick(g,1,1,r),
 lambda g,r:post_short_approval(g,1,r),
 lambda g,r:release_document_reservations(g,"PICK_WAVE",1,"admin","reason"),
 lambda g,r:post_reservation(g,"CREATE",r,"admin"),
 lambda g,r:reserve_wave_sources(g,1,"admin"),
 lambda g,r:apply_mes_movements(g,1,r,"admin"),
 lambda g,r:release_supply(g,1,r),
 lambda g,r:calculate_supply(g,1,r),
 lambda g,r:post_mes_task(g,"CONFIRM",{},r),
 lambda g,r:post_terminal_quality(g,"internal",r),
])
def test_adapter_never_returns_legacy_opt_out(call):
 with pytest.raises(StockPostingError)as caught:call(Inactive(),SimpleNamespace(operation_id="BOUND148"))
 assert caught.value.code=="STOCK_RELEASE_NOT_ACTIVE"
