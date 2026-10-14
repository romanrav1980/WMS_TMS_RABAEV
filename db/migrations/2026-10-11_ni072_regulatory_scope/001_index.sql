create index RRL_EVENT_OUTBOX_WARE_I on RRL_EVENT_OUTBOX(
 json_value(PAYLOAD_JSON,'$.warehouse_id' returning number null on error));
/
