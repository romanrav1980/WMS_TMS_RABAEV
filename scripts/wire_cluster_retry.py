from pathlib import Path
p=Path("api/wms_api_server/app/schemas.py");s=p.read_text(encoding="utf-8-sig")
start=s.index("class ClusterCreateTaskRequest(");end=s.index("\n\nclass ",start)
section=s[start:end]
section=section.replace('    stdate: date =','    operation_id: str = Field(min_length=1,max_length=100,pattern=r"^[A-Za-z0-9_.:-]+$")\n    stdate: date =')
section=section.replace("    vehicle: str | None = None","    vehicle: str | None = Field(default=None,max_length=50)")
section=section.replace("    driver_id: int | None = None","    driver_id: int | None = Field(default=None,ge=0)")
section=section.replace("    dock: str | None = None","    dock: str | None = Field(default=None,max_length=50)")
section=section.replace("    ware_ids: list[int] | None = None","    ware_ids: list[int] | None = Field(default=None,max_length=100)")
s=s[:start]+section+s[end:];p.write_text(s,encoding="utf-8")
p=Path("api/wms_api_server/app/services/transport_service.py");s=p.read_text(encoding="utf-8-sig")
start=s.index("        if not sts:",s.index("    def create_task_from_cluster("));end=s.index("        from ..modules.transport.public import create_existing_cluster",start)
s=s[:start]+s[end:]
s=s.replace('[str(row["ST_NUMBER"]) for row in sts],user_id)','[str(row["ST_NUMBER"]) for row in sts],user_id,req.operation_id,req.ware_ids)')
p.write_text(s,encoding="utf-8")
