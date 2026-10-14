import sys,os,json
from pathlib import Path
from unittest.mock import patch,Mock
sys.path.insert(0,'api/wms_api_server')
from app.modules.integrations.infrastructure.regulatory_runtime import regulatory_runtime_status,build_regulatory_adapter
from app.services.outbox_service import OutboxService
rows=[]
for mode,allow,expected in [('DISABLED','0','REGULATORY_DISABLED'),('REAL','0','PRODUCTION_CONNECTOR_NOT_IMPLEMENTED'),('MOCK','0','MOCK_NOT_ALLOWED'),('MOCK','1','SIMULATION_ONLY'),('UNKNOWN','0','UNSUPPORTED_MODE')]:
 with patch.dict(os.environ,{'NICORA_REGULATORY_MODE':mode,'NICORA_ALLOW_REGULATORY_MOCK':allow}):
  status=regulatory_runtime_status();assert status['reason_code']==expected and not status['real_external_ack'];rows.append(status)
  if mode=='REAL':
   adapter=build_regulatory_adapter();gateway=Mock();journal=Mock();journal.recover_one.return_value=None
   service=OutboxService(gateway=gateway,adapter=adapter,journal=journal);service.delivery=Mock()
   result=service.process_next('diagnostic-only','CRPT');assert result['reason_code']==expected and result['pending_events_preserved'];service.delivery.claim.assert_not_called()
Path('reports/nicora/2026-10-13/codex/NI043/connection_diagnostics.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2),encoding='utf-8')
print('PASS five modes, REAL actionable reason, no claim/send; no Oracle or external calls')
