"""A login capability must not turn scoped operational grants into flat rights."""
from contextlib import contextmanager
import pytest
from api.wms_api_server.app.auth import AdminUser
from api.wms_api_server.app.modules.platform.infrastructure.admin_shell import authorize_admin_shell
from api.wms_api_server.app.modules.platform.infrastructure.metadata_io import MetadataError


class Gateway:
    def __init__(self, allowed):
        self.allowed, self.calls = allowed, []
    @contextmanager
    def transaction(self, label):
        yield self
    def execute(self, sql, **binds):
        self.calls.append((sql, binds))
    def fetchone(self):
        return (self.allowed,)


def test_shell_only_adds_login_capability():
    user = AdminUser("scoped", "Scoped", "NONE", set())
    gateway = Gateway(1)
    result = authorize_admin_shell(gateway, user)
    assert result.permissions == {"wms_admin_login"} and user.permissions == set()
    assert gateway.calls[0][0] == "set transaction read only"
    assert "'PLATFORM',null" in gateway.calls[1][0]


def test_revoked_platform_grant_denies_next_login():
    with pytest.raises(MetadataError) as error:
        authorize_admin_shell(Gateway(0), AdminUser("scoped", "Scoped", "NONE", set()))
    assert error.value.status == 403


def test_legacy_login_and_global_admin_remain_compatible():
    for permissions in ({"wms_admin_login"}, {"*"}):
        gateway = Gateway(0)
        user = AdminUser("legacy", "Legacy", "OLD", permissions)
        assert authorize_admin_shell(gateway, user) is user and gateway.calls == []
