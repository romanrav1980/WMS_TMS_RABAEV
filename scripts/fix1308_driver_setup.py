from pathlib import Path
p=Path("scripts/setup1306_driver.py");s=p.read_text(encoding="utf-8")
s=s.replace(' r=client.get("/api/transport/driver-bindings/10018")',' r=client.post("/api/admin/rights/groups/OWN1306_DRIVER/rights",json={"right_name":"driver_return_accept","description":"Owned B03 driver binding"});r.raise_for_status()\n r=client.get("/api/transport/driver-bindings/10018")')
p.write_text(s,encoding="utf-8")
p=Path("admin/wms_admin_frontend/src/components/DriverMobilePage.tsx");s=p.read_text(encoding="utf-8").replace('import "../features/transport/DriverWorkspace.css";\n','');p.write_text(s,encoding="utf-8")
p=Path("admin/wms_admin_frontend/src/features/transport/DriverLogin.tsx");s=p.read_text(encoding="utf-8");p.write_text('import "./DriverWorkspace.css";\n'+s,encoding="utf-8")
