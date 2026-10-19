import pytest
from pydantic import ValidationError
from api.wms_api_server.app.modules.integrations.contracts_trade_transport import TransportDocumentResult

def value():
 return dict(operation_id='op',source_id='SAP',external_event_id='event',expected_trip_version=1,expected_binding_version=1,document_version=1,document_status='READY',external_document_id='DOC1',manifest_signature='A'*64,occurred_at='2026-10-19T14:00:00+03:00')

@pytest.mark.parametrize('change',['no_document','error_no_reason','naive_time','invalid_hash','bool_version'])
def test_transport_document_requires_business_evidence(change):
 body=value()
 if change=='no_document':body['external_document_id']=None
 elif change=='error_no_reason':body['document_status']='ERROR'
 elif change=='naive_time':body['occurred_at']='2026-10-19T14:00:00'
 elif change=='invalid_hash':body['manifest_signature']='a'*64
 else:body['document_version']=True
 with pytest.raises(ValidationError):TransportDocumentResult.model_validate(body)
