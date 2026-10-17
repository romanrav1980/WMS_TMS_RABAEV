"""Explicit wiki allowlist -> preview -> durable draft. Never arbitrary path or auto-publish."""
import hashlib
import json
from pathlib import Path
from typing import Any
from .access_read import AccessRead
from .metadata_io import MetadataError, native_command, receipt, json_object

class WikiPublication:
    def __init__(self, gateway: Any, root: Path) -> None:
        self.gateway = gateway
        self.root = root.resolve()
        self.manifest = json.loads((self.root/"docs/help/wiki-sources.json").read_text(encoding="utf-8"))

    def sources(self, actor: str) -> list[dict[str,Any]]:
        AccessRead(self.gateway).read(actor,"select 1 from dual",permission="knowledge_publish")
        return [{k:row[k] for k in ("source_id","article_id","title","summary","status","owner")} for row in self.manifest]

    def preview(self, actor: str, source_id: str) -> dict[str,Any]:
        self.sources(actor)
        source = next((row for row in self.manifest if row["source_id"]==source_id),None)
        if source is None: raise MetadataError("WIKI_SOURCE_NOT_ALLOWED",404)
        path = (self.root/source["path"]).resolve()
        if not path.is_relative_to(self.root/"wiki") or path.suffix!=".md" or path.stat().st_size>200000:
            raise MetadataError("WIKI_SOURCE_NOT_ALLOWED",422)
        raw = path.read_bytes()
        text = raw.decode("utf-8-sig")
        marker = "## "+source["section"]
        sections = text.split(marker,1)
        if len(sections)!=2: raise MetadataError("WIKI_SECTION_CHANGED",409)
        body = sections[1].split("\n## ",1)[0].strip()
        if not body or len(body)>20000: raise MetadataError("WIKI_SECTION_SIZE",422)
        return {k:source[k] for k in ("source_id","article_id","space_id","title","summary","status","owner")} | {
            "body":body,"source_revision":hashlib.sha256(raw).hexdigest(),"sources":[source["path"]],"related":[],"required_permissions":[]}

    def import_draft(self, actor: str, request: dict[str,Any]) -> dict[str,Any]:
        self.sources(actor)
        fingerprint = hashlib.sha256(json.dumps(request,sort_keys=True,ensure_ascii=False,separators=(",",":")).encode("utf-8")).hexdigest()
        try:
            previous = receipt(self.gateway,"KNOWLEDGE",actor,request["operation_id"])
        except MetadataError as error:
            if error.status!=404: raise
        else:
            rows = self.gateway.fetch_all("select PAYLOAD_JSON from RRL_KNOWLEDGE_REV where ARTICLE_ID=:id and VERSION_NO=:version",
                                          {"id":previous["object_id"],"version":previous["version"]})
            if not rows or json_object(rows[0]["payload_json"]).get("import_request_hash")!=fingerprint:
                raise MetadataError("OPERATION_CONFLICT",409)
            return previous | {"replayed":True}
        preview = self.preview(actor,request["source_id"])
        if preview["source_revision"]!=request["source_revision"]:
            raise MetadataError("WIKI_SOURCE_CHANGED_RECONCILE_PREVIOUS",409,False)
        payload = {k:preview[k] for k in ("article_id","space_id","title","summary","body","sources","related","required_permissions","source_id","source_revision")}
        payload.update(expected_version=request["expected_version"],reason=request["reason"],import_request_hash=fingerprint)
        return native_command(self.gateway,"KNOWLEDGE",actor,{"operation_id":request["operation_id"],"command_type":"ARTICLE_SAVE","payload":payload})
