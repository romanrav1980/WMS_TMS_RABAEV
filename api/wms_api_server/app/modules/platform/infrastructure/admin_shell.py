"""A PLATFORM login grant opens the shell without flattening warehouse rights."""
from typing import Any
import oracledb
from .authentication import AdminUser
from .metadata_io import MetadataError


def authorize_admin_shell(gateway: Any, user: AdminUser) -> AdminUser:
    if "*" in user.permissions or "wms_admin_login" in user.permissions:
        return user
    try:
        with gateway.transaction("Current PLATFORM admin shell login READ ONLY") as cursor:
            cursor.execute("set transaction read only")
            cursor.execute("select RRL_ACCESS_API.allowed(:actor,'wms_admin_login','PLATFORM',null) from dual",
                           actor=user.username)
            row = cursor.fetchone()
            if row is None or row[0] != 1:
                raise MetadataError("ADMIN_LOGIN_SCOPE_REQUIRED", 403)
    except oracledb.DatabaseError as error:
        raise MetadataError("ADMIN_LOGIN_SCOPE_UNAVAILABLE", 503) from error
    return AdminUser(user.username, user.display_name, user.user_group,
                     user.permissions | {"wms_admin_login"})
