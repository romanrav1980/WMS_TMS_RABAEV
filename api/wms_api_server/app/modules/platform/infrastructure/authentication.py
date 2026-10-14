"""Compatibility adapter to the existing Oracle/RUSERS authentication authority."""
from ....auth import AdminUser, require_permission, STOCK_RESERVATION_VIEW_PERMISSION

__all__ = ["AdminUser", "require_permission", "STOCK_RESERVATION_VIEW_PERMISSION"]

from ....auth import get_current_admin as get_current_user
