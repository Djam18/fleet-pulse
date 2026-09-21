from .inspection_admin import InspectionReportAdmin
from .maintenance_admin import MaintenanceScheduleAdmin
from .ticket_admin import NotificationAdmin, StatusChangeRequestAdmin
from .trip_admin import TripLogAdmin
from .vehicle_admin import VehicleAdmin

__all__ = [
    'VehicleAdmin',
    'TripLogAdmin',
    'MaintenanceScheduleAdmin',
    'InspectionReportAdmin',
    'StatusChangeRequestAdmin',
    'NotificationAdmin',
]
