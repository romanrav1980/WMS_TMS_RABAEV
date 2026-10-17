"""Composition of native commands and bounded read models; no alternate policy."""
from typing import Any
from .access_read import AccessRead
from .metadata_io import native_command, receipt
from .knowledge_read import KnowledgeRead

class AccessMetadataService(AccessRead):
    def command(self, actor: str, command: dict[str,Any]) -> dict[str,Any]:
        return native_command(self.gateway,"ACCESS",actor,command)
    def receipt(self, actor: str, operation_id: str) -> dict[str,Any]:
        return receipt(self.gateway,"ACCESS",actor,operation_id)

class KnowledgeMetadataService(KnowledgeRead):
    def command(self, actor: str, command: dict[str,Any]) -> dict[str,Any]:
        return native_command(self.gateway,"KNOWLEDGE",actor,command)
    def receipt(self, actor: str, operation_id: str) -> dict[str,Any]:
        return receipt(self.gateway,"KNOWLEDGE",actor,operation_id)
