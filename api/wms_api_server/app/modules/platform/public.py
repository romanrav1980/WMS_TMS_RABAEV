"""Shared infrastructure contracts; no business quantity decisions."""
from .infrastructure.configuration import stock_configuration_transaction

from .infrastructure.authentication import AdminUser, require_permission, STOCK_RESERVATION_VIEW_PERMISSION

from .infrastructure.oracle_json import read_oracle_json
from .infrastructure.authentication import get_current_user

from .application.knowledge import KnowledgeService
from .infrastructure.knowledge_catalog import PublishedKnowledge
from .api.knowledge_routes import knowledge_router, knowledge_service, knowledge_user
from .contracts import AccessScope, RoleAssignment

from .api.metadata_routes import access_router, knowledge_admin_router, metadata_user, access_service, knowledge_admin_service
from .infrastructure.metadata_services import AccessMetadataService, KnowledgeMetadataService
from .infrastructure.knowledge_read import NativePublishedHelp
from .infrastructure.metadata_io import MetadataError

from .api.knowledge_import_routes import wiki_publication_router, wiki_publication_service
from .infrastructure.wiki_publication import WikiPublication

from .infrastructure.independent_decision import assert_independent_decision


def authorize_admin_shell(user: AdminUser) -> AdminUser:
    from ...oracle_gateway import OracleGateway
    from .infrastructure.admin_shell import authorize_admin_shell as authorize
    return authorize(OracleGateway(), user)
