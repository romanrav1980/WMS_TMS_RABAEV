# Oracle native JSON в существующем SAP обмене
10.10.2026, выявлено при NI06.2 REUSE. ARTMAS импорт создал новый own article, WarehouseSupplyOrder then500 before any inventory. Direct original service traceback: UNITS_JSON already list, json.loads(list) TypeError. After decoding fix source then ORA-01745 for reserved bind :raw. No partial source/order persisted on rejected transactions.

Shared platform read_oracle_json accepts native dict/list/scalar, JSON text and LOB; applied to current supply message replay/aggregation/UOM, article apply/replay and receipt staged domain. Existing source binding renamed xml_raw, aggregation code_raw/agg_level. No transport/XML mapping replaced.

Same original source cdbf4c0962 continued: ARTMAS source APPLIED, supply order5b3e036751484ec0b1eb0a746187f4d4, actual SAP receipt BOX24 and warehouse task, physical shipment/store receipt24. Original helper replay supports native JSON result. This is assumed gateway technical source, no real SAP ACK.
