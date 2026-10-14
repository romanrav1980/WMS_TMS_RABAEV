from pathlib import Path
p=Path("api/wms_api_server/app/modules/inventory/api/receiving_routes.py")
t=p.read_text(encoding="utf-8")
assert "    defer_wait_cell:" not in t
t=t.replace('class WarehouseReceiptSettings(BaseModel):','class WarehouseReceiptSettings(BaseModel):\n    defer_wait_cell: str | None = Field(default=None, min_length=1, max_length=50)')
t=t.replace('for optional in ("hu_cell_height_unit",','for optional in ("defer_wait_cell","hu_cell_height_unit",')
p.write_text(t,encoding="utf-8")
p=Path("api/wms_api_server/app/modules/inventory/infrastructure/configuration.py")
t=p.read_text(encoding="utf-8")
anchor='            if "outgoing_qc_mode" in body:'
assert anchor in t and '"defer_wait_cell" in body' not in t
t=t.replace(anchor,'''            if "defer_wait_cell" in body:
                cur.execute("update RRL_RECEIPT_WARE_SETTINGS set DEFER_WAIT_CELL=:cell where WARE_ID=:w", {"cell": body["defer_wait_cell"], "w": warehouse})
'''+anchor)
p.write_text(t,encoding="utf-8")
print("761 optional waiting-cell setting wired; omission preserves existing value")
