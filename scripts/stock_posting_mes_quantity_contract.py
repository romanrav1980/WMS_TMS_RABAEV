"""Preserve MES physical quantities before Oracle receives their facts."""
import json
from pathlib import Path
out={}
p=Path("api/wms_api_server/app/schemas.py");s=p.read_text(encoding="utf-8")
for name,replacements in {
 "MesRawIssueRequest":{"quantity: float":"quantity: Decimal = Field(gt=0, max_digits=27, decimal_places=9, allow_inf_nan=False)"},
 "MesCompletionPallet":{"quantity: float | None = None":"quantity: Decimal | None = Field(default=None, gt=0, max_digits=27, decimal_places=9, allow_inf_nan=False)",
 "pack_count: float | None = None":"pack_count: Decimal | None = Field(default=None, ge=0, max_digits=27, decimal_places=9, allow_inf_nan=False)"},
 "MesCompleteOrderRequest":{"fact_qty: float":"fact_qty: Decimal = Field(gt=0, max_digits=27, decimal_places=9, allow_inf_nan=False)"}
}.items():
 start=s.index("class "+name+"(BaseModel):");end=s.index("\n\nclass ",start+1);part=s[start:end]
 for old,new in replacements.items():
  assert part.count(old)==1,(name,old)
  part=part.replace(old,new,1)
 s=s[:start]+part+s[end:]
out[str(p)]=s
p=Path("api/wms_api_server/app/services/mes_service.py");s=p.read_text(encoding="utf-8")
s=s.replace("payload = [_model_dict(pallet) for pallet in request.pallets]","payload = [pallet.model_dump(mode='json') for pallet in request.pallets]",1)
s=s.replace("import json\n","import json\nfrom decimal import Decimal\n",1)
s=s.replace("if fact_qty is None or float(fact_qty) <= 0:","if fact_qty is None or Decimal(str(fact_qty)) <= 0:",1)
s=s.replace("quantity=float(fact_qty),","quantity=Decimal(str(fact_qty)),",1)
# Private legacy reservation builders are never a second executor after activation.
for needle in ("        reservation_id = self._next_sequence_value(\"RRL_STOCK_RESERVATION_SQ\", \"RESERVATION_ID\")",):
 assert s.count(needle)==2
 s=s.replace(needle,"        self._assert_legacy_reservation_builder()\n"+needle)
needle="    def _create_soft_raw_reservation("
assert s.count(needle)==1
s=s.replace(needle,'''    def _assert_legacy_reservation_builder(self) -> None:
        rows = self.gateway.fetch_all("select STATE from RRL_STOCK_RELEASE where RELEASE_ID=1")
        if not rows or rows[0]["state"] != "PREPARED":
            raise HTTPException(409, detail={"code": "MES_RESERVATION_POSTING_REQUIRED"})

'''+needle,1)
out[str(p)]=s
print(json.dumps(out,ensure_ascii=True))
