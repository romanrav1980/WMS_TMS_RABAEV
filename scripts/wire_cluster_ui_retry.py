from pathlib import Path
p=Path("admin/wms_admin_frontend/src/components/TransportDispatchPage.tsx");s=p.read_text(encoding="utf-8-sig")
s='import { submitCluster } from "../features/transport";\n'+s
start=s.index('      const res = await apiFetch<',s.index('  async function handleCreateFromCluster('))
end=s.index('      if (res.warnings.length',start)
s=s[:start]+'''      const res = await submitCluster(apiFetch,
        {api: API_BASE, actor: API_BASIC_AUTH.split(":", 1)[0]},params.raion,{
          stdate: stDate, transtype: params.transtype, vehicle: params.vehicle || null,
          driver_id: params.driver_id, dock: params.dock || null, ware_ids: null,
        });
'''+s[end:]
p.write_text(s,encoding="utf-8")
