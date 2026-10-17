"""Real encrypted local OPC UA server; not physical hardware or Oracle acceptance."""
import asyncio
from contextlib import asynccontextmanager
from datetime import datetime, timedelta, timezone
import hashlib
import ipaddress
import json
from pathlib import Path
import socket
from types import SimpleNamespace

import pytest
pytest.importorskip("asyncua")
from asyncua import Server, ua
from asyncua.common.structures104 import new_struct, new_struct_field
from cryptography import x509
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.x509.oid import NameOID, ExtendedKeyUsageOID

from api.wms_api_server.app.modules.integrations.infrastructure.scale_opc_profile import OpcScaleProfile, SCALES_V2
from api.wms_api_server.app.modules.integrations.infrastructure.scale_opc_client import Opc40200Client
from api.wms_api_server.app.modules.integrations.infrastructure.scale_device_lease import SqliteScaleDeviceLease
from api.wms_api_server.app.modules.integrations.infrastructure.scale_bundle_journal import SqliteScaleBundleJournal
from api.wms_api_server.app.modules.integrations.application.scale_opc_capture import OpcStoreCapture
from api.wms_api_server.app.modules.integrations.contracts_scales import ScaleGatewayError


@pytest.fixture(autouse=True)
def isolated_opc_test_credentials(monkeypatch):
    for name in ("STORE_SCALE_OPC_USER", "STORE_SCALE_OPC_PASSWORD", "STORE_SCALE_OPC_KEY_PASSWORD"):
        monkeypatch.delenv(name, raising=False)


def certificate(root, name, uri):
    key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    subject = x509.Name([x509.NameAttribute(NameOID.COMMON_NAME, name)])
    now = datetime.now(timezone.utc)
    cert = (x509.CertificateBuilder().subject_name(subject).issuer_name(subject).public_key(key.public_key())
        .serial_number(x509.random_serial_number()).not_valid_before(now-timedelta(minutes=1))
        .not_valid_after(now+timedelta(days=1))
        .add_extension(x509.SubjectAlternativeName([x509.UniformResourceIdentifier(uri),
                       x509.DNSName("localhost"), x509.IPAddress(ipaddress.ip_address("127.0.0.1"))]), False)
        .add_extension(x509.BasicConstraints(ca=False, path_length=None), True)
        .add_extension(x509.KeyUsage(True, True, True, True, False, False, False, False, False), True)
        .add_extension(x509.ExtendedKeyUsage([ExtendedKeyUsageOID.SERVER_AUTH, ExtendedKeyUsageOID.CLIENT_AUTH]), False)
        .sign(key, hashes.SHA256()))
    cp, kp = root/(name+".der"), root/(name+".pem")
    cp.write_bytes(cert.public_bytes(serialization.Encoding.DER))
    kp.write_bytes(key.private_bytes(serialization.Encoding.PEM, serialization.PrivateFormat.PKCS8, serialization.NoEncryption()))
    return cp, kp, cert.fingerprint(hashes.SHA256()).hex().upper()


@asynccontextmanager
async def opc_fixture(root):
    server = Server()
    await server.init()
    with socket.socket() as sock:
        sock.bind(("127.0.0.1", 0))
        port = sock.getsockname()[1]
    endpoint = "opc.tcp://127.0.0.1:"+str(port)+"/scale/"
    server_uri, client_uri = "urn:retailcase:test:scale", "urn:retailcase:test:gateway"
    sc, sk, fingerprint = certificate(root, "server", server_uri)
    cc, ck, _ = certificate(root, "client", client_uri)
    server.set_endpoint(endpoint)
    await server.set_application_uri(server_uri)
    await server.load_certificate(sc)
    await server.load_private_key(sk)
    server.set_security_policy([ua.SecurityPolicyType.Basic256Sha256_SignAndEncrypt])
    index = await server.register_namespace(SCALES_V2)
    dtype, _ = await new_struct(server, index, "WeightType", [new_struct_field(f, ua.VariantType.Double) for f in ("Gross", "Net", "Tare")])
    await server.load_data_type_definitions()
    parent = await server.nodes.objects.add_object(index, "TestScale")
    state = dict(gross=0.0, stable=True, zero=True, overload=False, underload=False, tare_mode=0,
                 unit_id=4933453, quality=0, stale=False, source_old=False, tare=0.0)
    nodes, mapping = {}, {}
    fields = ["current_weight", "stable", "center_zero", "overload", "underload", "tare_mode", "engineering_units"]
    for field in fields:
        if field == "current_weight":
            value = ua.WeightType(Gross=0.0, Net=0.0, Tare=0.0)
            node = await parent.add_variable(index, field, value, datatype=dtype.nodeid)
        elif field == "engineering_units":
            node = await parent.add_variable(index, field, ua.EUInformation(NamespaceUri="urn:test:units", UnitId=4933453))
        elif field == "tare_mode":
            node = await parent.add_variable(index, field, 0)
        else:
            node = await parent.add_variable(index, field, False)
        nodes[field] = node
        mapping[field] = dict(namespace_uri=SCALES_V2, identifier_type="i", identifier=node.nodeid.Identifier)
        def callback(nodeid, attr, field=field):
            now = datetime.now(timezone.utc)
            if field == "current_weight":
                value = ua.WeightType(Gross=state["gross"], Net=state["gross"]-state["tare"], Tare=state["tare"])
            elif field == "engineering_units":
                value = ua.EUInformation(NamespaceUri="urn:test:units", UnitId=state["unit_id"])
            else:
                value = state["zero" if field == "center_zero" else field]
            dv = ua.DataValue(ua.Variant(value))
            dv.StatusCode = ua.StatusCode(state["quality"] if field == "current_weight" else 0)
            dv.ServerTimestamp = now-timedelta(seconds=10 if state["stale"] else 0)
            dv.SourceTimestamp = now-timedelta(seconds=20 if state["source_old"] or state["stale"] else 0)
            return dv
        server.set_attribute_value_callback(node.nodeid, callback)
    data = dict(model_namespace_uri=SCALES_V2, model_version="2.00", endpoint=endpoint,
                device_id="TEST.OPC.1", station_id="TEST.POST.1", application_uri=client_uri,
                server_application_uri=server_uri, nodes=mapping, unit_namespace_uri="urn:test:units",
                kg_unit_id=4933453, no_tare_mode=0,
                security=dict(client_certificate=cc.name, private_key=ck.name,
                              server_certificate=sc.name, server_sha256=fingerprint))
    profile_path = root/"profile.json"
    profile_path.write_text(json.dumps(data), encoding="utf-8")
    await server.start()
    try:
        yield OpcScaleProfile.load(profile_path), state
    finally:
        await server.stop()


def test_encrypted_real_opc_read_zero_then_capture_and_canonical_store_projection(tmp_path):
    async def scenario():
        async with opc_fixture(tmp_path) as (profile, state):
            reader = Opc40200Client(profile)
            await reader.connect()
            try:
                journal = SqliteScaleBundleJournal(tmp_path/"bundles.sqlite")
                service = OpcStoreCapture(reader, SqliteScaleDeviceLease(tmp_path/"lease.sqlite"), profile.data, profile.digest, journal)
                assert await service.observe_zero()
                state.update(gross=10.1, zero=False, source_old=True)
                packet, raw = await service.capture(dict(device_id="TEST.OPC.1", state="REQUESTED", request_id="req1",
                    load_operation_id="load1", store_address="store1", device_policy_version=1, calibration_ref="cal1"))
                from api.wms_api_server.app.modules.delivery.api.store_scale_routes import ScalePacket
                from api.wms_api_server.app.modules.integrations.contracts_scale_evidence import ScaleEvidence
                ScalePacket.model_validate_json(packet)
                assert ScaleEvidence.model_validate_json(raw).canonical_bytes() == raw
                body, evidence = json.loads(packet), json.loads(raw)
                assert len(body["samples"]) >= 5 and body["samples"][-1]["offset_ms"] >= 2000
                assert body["samples"][-1]["gross_weight_kg"] == "10.1"
                assert evidence["capture_sha256"] == hashlib.sha256(packet).hexdigest().upper()
                assert evidence["observations"][0]["values"]["current_weight"]["value"]["Gross"] == "10.1"
                assert evidence["zero_observation"]["values"]["current_weight"]["value"]["Gross"] == "0.0"
                assert service.zero is None
                assert journal.get("STORE_RECEIPT","TEST.OPC.1","req1") == (packet,raw)
                state.update(quality=ua.StatusCodes.BadNoCommunication)
                assert await service.capture(dict(device_id="TEST.OPC.1",state="REQUESTED",request_id="req1")) == (packet,raw)
            finally:
                await reader.disconnect()
    asyncio.run(scenario())


@pytest.mark.parametrize("change,code", [({"quality":ua.StatusCodes.BadNoCommunication},"QUALITY"),
    ({"quality":ua.StatusCodes.Uncertain},"QUALITY"), ({"stale":True},"TIME_STALE"),
    ({"unit_id":123},"KG_UNIT"), ({"overload":True},"RANGE"), ({"tare":1.0,"gross":2.0},"TARE"),
    ({"tare_mode":1},"TARE_MODE")])
def test_actual_opc_invalid_data_never_becomes_measurement(tmp_path, change, code):
    async def scenario():
        async with opc_fixture(tmp_path) as (profile, state):
            reader = Opc40200Client(profile)
            await reader.connect()
            try:
                state.update(change)
                with pytest.raises(ScaleGatewayError, match=code):
                    await reader.read()
            finally:
                await reader.disconnect()
    asyncio.run(scenario())


def test_real_opc_server_with_wrong_pin_is_never_trusted(tmp_path):
    async def scenario():
        async with opc_fixture(tmp_path) as (profile, state):
            profile.data["security"]["server_sha256"] = "0"*64
            reader = Opc40200Client(profile)
            with pytest.raises(ScaleGatewayError, match="CERTIFICATE_OR_URI"):
                await reader.connect()
    asyncio.run(scenario())


def test_reconnect_requires_new_zero_not_a_previous_connection_cache(tmp_path):
    async def scenario():
        async with opc_fixture(tmp_path) as (profile, state):
            reader = Opc40200Client(profile)
            await reader.connect()
            service = OpcStoreCapture(reader, SqliteScaleDeviceLease(tmp_path/"lease.sqlite"), profile.data, profile.digest)
            assert await service.observe_zero()
            service.reset_connection()
            state.update(gross=10.0, zero=False)
            await reader.disconnect()
            await reader.connect()
            try:
                with pytest.raises(ScaleGatewayError, match="ZERO_REQUIRED"):
                    await service.capture(dict(device_id=profile.data["device_id"], state="REQUESTED"))
            finally:
                await reader.disconnect()
    asyncio.run(scenario())


def test_real_opc_window_through_real_http_capture_and_evidence_delivery(tmp_path):
    from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
    import threading
    import time
    from tools.store_scale_opc_gateway import cycle
    from api.wms_api_server.app.modules.integrations.infrastructure.scale_evidence_http import HttpScaleEvidenceGateway
    from api.wms_api_server.app.modules.integrations.infrastructure.scale_outbox import SqliteScaleOutbox
    from api.wms_api_server.app.modules.integrations.application.scale_gateway import ScaleGatewayWorker
    captures, evidence_records = [], []
    request = dict(request_id="e2e1",device_id="TEST.OPC.1",state="REQUESTED",load_operation_id="load1",store_address="store1",
                   device_policy_version=1,calibration_ref="cal1",expires_at="2099-01-01T00:00:00+00:00")
    class Handler(BaseHTTPRequestHandler):
        def log_message(self,*args):
            pass
        def do_GET(self):
            self.reply({"items":[] if captures else [request]})
        def do_POST(self):
            body = self.rfile.read(int(self.headers["Content-Length"]))
            source = json.loads(body)
            sha = hashlib.sha256(json.dumps(source,ensure_ascii=True,sort_keys=True,separators=(",", ":")).encode()).hexdigest().upper()
            if self.path.endswith("/captures"):
                captures.append(body)
                identity = json.dumps([source["device_id"],source["capture_id"]],separators=(",", ":")).encode()
                result = dict(source,status="ARCHIVED",receipt_confirmed=False,
                    capture_key=hashlib.sha256(identity).hexdigest().upper(),source_sha256=sha,
                    gross_weight_kg=source["samples"][-1]["gross_weight_kg"])
            else:
                evidence_records.append(body)
                result = {key:source[key] for key in ("protocol_version","device_id","capture_id","capture_kind","capture_sha256")}
                result.update(status="ARCHIVED",binding="MATCHED",stock_posted=False,provenance="GATEWAY_REPORTED",evidence_sha256=sha)
            self.reply(result)
        def reply(self,data):
            self.send_response(200)
            self.send_header("Content-Type","application/json")
            self.end_headers()
            self.wfile.write(json.dumps(data).encode())
    http = ThreadingHTTPServer(("127.0.0.1",0),Handler)
    thread = threading.Thread(target=http.serve_forever,daemon=True)
    thread.start()
    async def scenario():
        async with opc_fixture(tmp_path) as (profile,state):
            reader = Opc40200Client(profile)
            await reader.connect()
            try:
                journal = SqliteScaleBundleJournal(tmp_path/"bundles.sqlite")
                capture = OpcStoreCapture(reader,SqliteScaleDeviceLease(tmp_path/"leases.sqlite"),profile.data,profile.digest,journal)
                api = HttpScaleEvidenceGateway("http://127.0.0.1:"+str(http.server_port),"test-sender","test-only",allow_loopback_http=True)
                box, rawbox = SqliteScaleOutbox(tmp_path/"capture.sqlite"),SqliteScaleOutbox(tmp_path/"raw.sqlite",max_packet_bytes=131072)
                async def place_load():
                    while capture.zero is None:
                        await asyncio.sleep(.01)
                    state.update(gross=10.1,zero=False)
                placement = asyncio.create_task(place_load())
                await cycle(api,ScaleGatewayWorker(api,box,"TEST.OPC.1",time.time),capture,rawbox,journal)
                await placement
                assert len(captures) == len(evidence_records) == 1
                assert box.claim(time.time()) is None and rawbox.claim(time.time()) is None
            finally:
                await reader.disconnect()
    try:
        asyncio.run(scenario())
    finally:
        http.shutdown()
        http.server_close()
        thread.join(timeout=2)


def test_assembly_auto_gate_waits_for_real_change_before_stable_after_series(tmp_path):
    from decimal import Decimal
    from api.wms_api_server.app.modules.integrations.application.scale_opc_window import collect_opc_window
    async def scenario():
        async with opc_fixture(tmp_path) as (profile,state):
            reader = Opc40200Client(profile)
            await reader.connect()
            try:
                state.update(gross=10.0,zero=False)
                lease = SqliteScaleDeviceLease(tmp_path/"device.sqlite")
                import time
                token = lease.acquire("TEST.OPC.1",time.time(),10)
                async def place():
                    await asyncio.sleep(.75)
                    state.update(gross=11.0)
                placement = asyncio.create_task(place())
                observations, offsets = await collect_opc_window(reader,
                    lambda:lease.renew("TEST.OPC.1",token,time.time(),10),6,
                    before=Decimal("10"),min_change=Decimal(".1"))
                await placement
                assert len(observations) >= 5 and offsets[-1] >= 2000
                assert all(item.gross == Decimal("11") for item in observations)
                lease.release("TEST.OPC.1",token)
            finally:
                await reader.disconnect()
    asyncio.run(scenario())


def test_real_assembly_before_and_changed_after_have_v11_reference_without_fake_zero(tmp_path):
    from api.wms_api_server.app.modules.integrations.application.assembly_opc_capture import OpcAssemblyCapture
    from api.wms_api_server.app.modules.inventory.contracts_assembly_scale import AssemblyCapture
    from api.wms_api_server.app.modules.integrations.contracts_scale_evidence import AssemblyScaleEvidence
    async def scenario():
        async with opc_fixture(tmp_path) as (profile,state):
            reader = Opc40200Client(profile)
            await reader.connect()
            try:
                state.update(gross=.5,zero=False)
                journal = SqliteScaleBundleJournal(tmp_path/"bundles.sqlite")
                capture = OpcAssemblyCapture(reader,SqliteScaleDeviceLease(tmp_path/"lease.sqlite"),profile.data,profile.digest,journal)
                request = dict(device_id=profile.data["device_id"],session_id="session1",step_id="step1",capture_id="BEFORE.1",phase="BEFORE",
                    device_policy_version=1,calibration_ref="cal1",expires_at="2099-01-01T00:00:00+00:00",
                    expected_before_kg=".5",min_delta_kg=".1",confirmation_mode="AUTO",tare_capture_key="A"*64)
                before,raw_before = await capture.capture(request)
                assert journal.get("WAREHOUSE_ASSEMBLY",request["device_id"],"BEFORE.1") == (before,raw_before)
                assert AssemblyCapture.model_validate_json(before).phase == "BEFORE"
                assert AssemblyScaleEvidence.model_validate_json(raw_before).canonical_bytes() == raw_before
                request.update(phase="AFTER",capture_id="AFTER.1")
                async def place_load():
                    await asyncio.sleep(.75)
                    state.update(gross=1.5)
                placement = asyncio.create_task(place_load())
                after,raw_after = await capture.capture(request,timeout=6)
                await placement
                assert AssemblyCapture.model_validate_json(after).samples[-1].weight_kg == "1.5"
                assert journal.get("WAREHOUSE_ASSEMBLY",request["device_id"],"AFTER.1") == (after,raw_after)
                state.update(quality=ua.StatusCodes.BadNoCommunication)
                assert await capture.capture(request) == (after,raw_after)
                evidence = AssemblyScaleEvidence.model_validate_json(raw_after)
                assert evidence.canonical_bytes() == raw_after
                assert evidence.zero_reference.tare_capture_key == "A"*64
                assert "zero_observation" not in json.loads(raw_after)
                assert all(obs.values.current_weight.value["Gross"] == "1.5" for obs in evidence.observations)
            finally:
                await reader.disconnect()
    asyncio.run(scenario())


def test_real_reconciliation_reads_current_unchanged_gross_and_emits_distinct_raw12(tmp_path):
    from api.wms_api_server.app.modules.integrations.application.assembly_opc_capture import OpcAssemblyCapture
    from api.wms_api_server.app.modules.inventory.contracts_assembly_recovery import AssemblyReconciliationCapture
    from api.wms_api_server.app.modules.integrations.contracts_scale_evidence import AssemblyReconciliationEvidence
    async def scenario():
        async with opc_fixture(tmp_path)as(profile,state):
            state.update(gross=.5,zero=False)
            reader=Opc40200Client(profile);await reader.connect()
            try:
                journal=SqliteScaleBundleJournal(tmp_path/'bundles.sqlite')
                capture=OpcAssemblyCapture(reader,SqliteScaleDeviceLease(tmp_path/'lease.sqlite'),profile.data,profile.digest,journal)
                request=dict(device_id=profile.data['device_id'],session_id='s',step_id='step',capture_id='recon.capture',phase='RECONCILE',reconciliation_id='recon.request',device_policy_version=1,calibration_ref='cal',expires_at='2099-01-01T00:00:00+00:00',expected_before_kg='.5',min_delta_kg='1',tare_capture_key='A'*64)
                body,raw=await capture.capture(request,timeout=3)
                assert AssemblyReconciliationCapture.model_validate_json(body).samples[-1].weight_kg=='0.5'
                evidence=AssemblyReconciliationEvidence.model_validate_json(raw)
                assert evidence.canonical_bytes()==raw and evidence.protocol_version=='1.2'
                assert evidence.zero_reference.phase=='RECONCILE'and evidence.zero_reference.reconciliation_id=='recon.request'
                assert 'zero_observation'not in json.loads(raw)
                assert journal.get('WAREHOUSE_ASSEMBLY_RECON',profile.data['device_id'],'recon.capture')==(body,raw)
            finally:await reader.disconnect()
    asyncio.run(scenario())
