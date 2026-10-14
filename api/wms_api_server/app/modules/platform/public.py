"""Shared infrastructure contracts; no business quantity decisions."""
from .infrastructure.configuration import stock_configuration_transaction

from .infrastructure.authentication import AdminUser, require_permission, STOCK_RESERVATION_VIEW_PERMISSION

from .infrastructure.oracle_json import read_oracle_json
from .infrastructure.authentication import get_current_user
