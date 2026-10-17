
# TEST1032: encrypted OPC → actual HTTP → native

15.10.2026, `scripts/assembly_opc_native_smoke.py` PASS. Root/fixture owner explicitly authorized only BEFORE0.5kg and out-of-policy AFTER3.5kg for TEST1032. Real encrypted localhost OPC server generated DataValues; production read-only client, physical-device lease, atomic bundle, HTTPS-adapter code with explicit loopback HTTP exception, actual WMS API and Oracle package were used. This is protocol/native integration, not physical weighing.

BEFORE0.5 produced ARMED; AFTER3.5 produced DISCREPANCY/BLOCKED as expected against quantity1 policy0.99..1.01kg. Both immutable capture archive ACKs and raw1.1 MATCHED ACKs passed exact identity/hash/weight validation. No ASM15.PICK1032 stock operation or step-use was created; source physical/hard/version snapshot remained exactly equal. INVALID0. Fresh slow-SQL interval had no records; retain PK/fixed-device bounded reads, no new index justified by this case.

Reports: [opc-native-http-report.json](opc-native-http-report.json). Immutable TEST capture/raw/label/audit history intentionally remains, tagged SIMULATED_TEST_LABEL_NOT_PHYSICAL / TEST_FIXTURE_NOT_HARDWARE. Sender password was read only from ignored runtime secrets and not printed. The fixed runner refuses another run once BEFORE is no longer pending; it never invents replacement IDs.
