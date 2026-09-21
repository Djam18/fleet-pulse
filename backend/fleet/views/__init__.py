from .auth import (
    FleetLoginView,
    FleetLogoutView,
    FleetPasswordResetCompleteView,
    FleetPasswordResetConfirmView,
    FleetPasswordResetDoneView,
    FleetPasswordResetView,
    FleetRegisterView,
)
from .dashboard import dashboard_view
from .inspections import inspection_list_view
from .maintenance import maintenance_list_view
from .telematics import telematics_stream_view
from .trips import trip_list_view
from .vehicles import vehicle_detail_view, vehicle_list_view

__all__ = [
    'dashboard_view',
    'vehicle_list_view',
    'vehicle_detail_view',
    'trip_list_view',
    'maintenance_list_view',
    'inspection_list_view',
    'FleetLoginView',
    'FleetLogoutView',
    'FleetRegisterView',
    'FleetPasswordResetView',
    'FleetPasswordResetDoneView',
    'FleetPasswordResetConfirmView',
    'FleetPasswordResetCompleteView',
    'telematics_stream_view',
]
