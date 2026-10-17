"""Physical supply progress remains separate from original picking demand."""
from typing import Any
from .wave_queue_reads import WaveQueueReads

class ReplenishmentProgress:
    def __init__(self,gateway: Any) -> None:
        self.gateway=gateway

    def list_rows(self,wave_id: int,limit: int,actor: str | None = None) -> list[dict[str,Any]]:
        if actor is not None:
            return WaveQueueReads(self.gateway).wave(wave_id,actor,lambda bound: ReplenishmentProgress(bound).list_rows(wave_id,limit))
        return self.gateway.fetch_all("""select PICK_WAVE_REPLENISH_TASK_ID,PICK_WAVE_ID,PICK_TASK_ID,ARTICUL,TARGET_CELL_CODE,SOURCE_CELL_CODE,STATUS,WAIT_REASON,PLANNED_BASE,DEMAND_BASE,
            to_char(CONFIRMED_NUMBER,'TM9','NLS_NUMERIC_CHARACTERS=''.,''') CONFIRMED_BASE,
            (select to_char(greatest(0,p.QTY-nvl(p.FACT_QTY,0)),'TM9','NLS_NUMERIC_CHARACTERS=''.,''')
                from RRL_PICK_TASK p where p.PICK_TASK_ID=selected.PICK_TASK_ID and p.TASK_TYPE='CASE_PICK') CASE_ORDER_REMAINING_BASE,
            to_char(RRL_STOCK_REPL_CAPACITY.remaining_base_quantity(TARGET_CELL_CODE,ARTICUL,PICK_WAVE_REPLENISH_TASK_ID),
                'TM9','NLS_NUMERIC_CHARACTERS=''.,''') CAPACITY_AVAILABLE_BASE,
            to_char(greatest(0,PLANNED_NUMBER-CONFIRMED_NUMBER),'TM9','NLS_NUMERIC_CHARACTERS=''.,''') DELIVERY_REMAINING_BASE,
            to_char(greatest(0,DEMAND_NUMBER-CONFIRMED_NUMBER),'TM9','NLS_NUMERIC_CHARACTERS=''.,''') DEMAND_REMAINING_BASE
            from (
             select rt.PICK_WAVE_REPLENISH_TASK_ID,rt.PICK_WAVE_ID,rt.PICK_TASK_ID,rt.ARTICUL,
                    rt.TARGET_CELL_CODE,rt.SOURCE_CELL_CODE,rt.STATUS,rt.WAIT_REASON,
                    rt.QTY PLANNED_NUMBER,nvl(rt.DEMAND_BASE_QTY,rt.QTY) DEMAND_NUMBER,
                    to_char(rt.QTY,'TM9','NLS_NUMERIC_CHARACTERS=''.,''') PLANNED_BASE,
                    to_char(nvl(rt.DEMAND_BASE_QTY,rt.QTY),'TM9','NLS_NUMERIC_CHARACTERS=''.,''') DEMAND_BASE,
                    nvl((select sum(m.BASE_QTY) from RRL_WAREHOUSE_TASK t
                         join RRL_WAREHOUSE_TASK_STOCK_MOVE m on m.TASK_ID=t.TASK_ID
                         where t.TASK_SOURCE='WAVE' and t.TASK_TYPE='REPLENISHMENT'
                           and t.SOURCE_TASK_ID=rt.PICK_WAVE_REPLENISH_TASK_ID),0) CONFIRMED_NUMBER
              from RRL_PICK_WAVE_REPLENISH_TASK rt where rt.PICK_WAVE_ID=:wave
              order by rt.PICK_WAVE_REPLENISH_TASK_ID fetch first :row_limit rows only
            ) selected""",{"wave":wave_id,"row_limit":limit})
