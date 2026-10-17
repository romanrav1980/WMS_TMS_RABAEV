"""Native archive owns authorization, identity, immutable bytes and binding reads."""
from typing import Any
import oracledb
from ....oracle_gateway import OracleGateway
from ...platform.public import read_oracle_json
from ..contracts_scale_evidence import ScaleEvidencePayload, ScaleEvidenceError


class ScaleEvidenceArchive:
    def __init__(self, gateway: OracleGateway) -> None:
        self.gateway = gateway

    def archive(self, body: ScaleEvidencePayload, actor: str) -> dict[str, Any]:
        return self._invoke("archive", [body.canonical_bytes().decode("utf-8"), actor], False)

    def read(self, kind: str, device: str, capture: str, actor: str) -> dict[str, Any]:
        return self._invoke("describe", [kind, device, capture, actor], True)

    def _invoke(self, method: str, arguments: list[Any], readonly: bool) -> dict[str, Any]:
        try:
            with self.gateway.transaction("OPC provenance " + method) as cursor:
                if readonly:
                    cursor.execute("set transaction read only")
                output = cursor.var(oracledb.DB_TYPE_CLOB)
                cursor.callproc("RRL_OPC_EVIDENCE_API." + method, [*arguments, output])
                return read_oracle_json(output.getvalue())
        except oracledb.DatabaseError as exc:
            code = exc.args[0].code
            status = 403 if code == 20882 else 404 if code == 20884 else 409 if 20800 <= code <= 20999 else 503
            raise ScaleEvidenceError(str(exc.args[0]).split("\n", 1)[0], status) from exc
