"""OPC40200 v2 read-only asyncua client; explicit trusted commissioning profile."""
import hashlib
import os
from typing import Any

from asyncua import Client, ua
from asyncua.crypto import security_policies
from asyncua.crypto.validator import CertificateValidator, CertificateValidatorOptions
from cryptography.hazmat.primitives import serialization

from ..contracts_scale_opc import OpcWeightObservation
from ..contracts_scales import ScaleGatewayError
from .scale_opc_profile import OpcScaleProfile, FIELDS, SCALES_V2
from .scale_opc_values import checked_values


class Opc40200Client:
    def __init__(self, profile: OpcScaleProfile) -> None:
        self.profile = profile
        self.client = Client(profile.data["endpoint"], timeout=3)
        self.client.application_uri = profile.data["application_uri"]
        self.nodes: dict[str, Any] = {}

    async def _security(self) -> None:
        data = self.profile.data
        if data.get("security", {}).get("test_loopback_no_security"):
            raise ScaleGatewayError("OPC_SIGN_AND_ENCRYPT_REQUIRED")
        await self.client.set_security(security_policies.SecurityPolicyBasic256Sha256,
            self.profile.certificate_path("client_certificate"), self.profile.certificate_path("private_key"),
            private_key_password=os.environ.get("STORE_SCALE_OPC_KEY_PASSWORD"),
            server_certificate=self.profile.certificate_path("server_certificate"),
            mode=ua.MessageSecurityMode.SignAndEncrypt)
        expected = data["security"]["server_sha256"].upper()
        validator = CertificateValidator(CertificateValidatorOptions.EXT_VALIDATION | CertificateValidatorOptions.PEER_SERVER)
        async def validate(cert: Any, description: Any) -> None:
            digest = hashlib.sha256(cert.public_bytes(serialization.Encoding.DER)).hexdigest().upper()
            if digest != expected or description.ApplicationUri != data["server_application_uri"]:
                raise ScaleGatewayError("OPC_SERVER_CERTIFICATE_OR_URI_MISMATCH")
            if digest in {str(value).upper() for value in data["security"].get("revoked_sha256", [])}:
                raise ScaleGatewayError("OPC_SERVER_CERTIFICATE_REVOKED")
            await validator.validate(cert, description)
        self.client.certificate_validator = validate
        user, password = os.environ.get("STORE_SCALE_OPC_USER"), os.environ.get("STORE_SCALE_OPC_PASSWORD")
        if bool(user) != bool(password):
            raise ScaleGatewayError("OPC_USER_IDENTITY_INCOMPLETE")
        if user:
            self.client.set_user(user)
            self.client.set_password(password)

    async def connect(self) -> None:
        try:
            await self._security()
            await self.client.connect()
            namespaces = await self.client.get_namespace_array()
            if SCALES_V2 not in namespaces:
                raise ScaleGatewayError("OPC40200_V2_NAMESPACE_MISSING")
            await self.client.load_data_type_definitions()
            for field in FIELDS:
                mapping = self.profile.data["nodes"][field]
                index = namespaces.index(mapping["namespace_uri"])
                identifier = mapping["identifier"]
                kind = ua.NodeIdType.String if mapping["identifier_type"] == "s" else ua.NodeIdType.Numeric
                self.nodes[field] = self.client.get_node(ua.NodeId(identifier, index, kind))
            dtype = await self.nodes["current_weight"].read_data_type()
            name = await self.client.get_node(dtype).read_browse_name()
            if name.Name != "WeightType" or namespaces[name.NamespaceIndex] != SCALES_V2:
                raise ScaleGatewayError("OPC_WEIGHTTYPE_MAPPING_REQUIRED")
            definition = await self.client.get_node(dtype).read_data_type_definition()
            if [field.Name for field in definition.Fields] != ["Gross", "Net", "Tare"]:
                raise ScaleGatewayError("OPC_WEIGHTTYPE_STRUCTURE_REJECTED")
            if any(field.DataType != ua.NodeId(ua.ObjectIds.Double, 0) or field.IsOptional or field.ValueRank != -1
                   for field in definition.Fields):
                raise ScaleGatewayError("OPC_WEIGHTTYPE_DOUBLE_FIELDS_REQUIRED")
            if await self.nodes["engineering_units"].read_data_type() != ua.NodeId(ua.ObjectIds.EUInformation, 0):
                raise ScaleGatewayError("OPC_EUINFORMATION_REQUIRED")
        except Exception:
            await self.disconnect()
            raise

    async def disconnect(self) -> None:
        self.nodes.clear()
        try:
            await self.client.disconnect()
        except Exception:
            pass

    async def read(self) -> OpcWeightObservation:
        if not self.nodes:
            raise ScaleGatewayError("OPC_NOT_CONNECTED")
        params = ua.ReadParameters()
        params.MaxAge = 0
        params.TimestampsToReturn = ua.TimestampsToReturn.Both
        params.NodesToRead = [ua.ReadValueId(NodeId=self.nodes[field].nodeid, AttributeId=ua.AttributeIds.Value) for field in FIELDS]
        try:
            values = await self.client.uaclient.read(params)
            observation = checked_values(dict(zip(FIELDS, values, strict=True)), self.profile.data)
            return observation
        except ScaleGatewayError:
            raise
        except Exception:
            raise ScaleGatewayError("OPC_READ_UNAVAILABLE", True) from None
