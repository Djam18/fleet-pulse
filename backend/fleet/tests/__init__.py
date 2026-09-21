from .test_admin import FleetAdminTests
from .test_auth import AuthenticationAndTelematicsTests
from .test_commands import SeedFleetCommandTests
from .test_models import MaintenanceScheduleModelTests, TripLogModelTests, VehicleModelTests
from .test_views import OperationsPagesTests

__all__ = [
    'VehicleModelTests',
    'TripLogModelTests',
    'MaintenanceScheduleModelTests',
    'OperationsPagesTests',
    'AuthenticationAndTelematicsTests',
    'FleetAdminTests',
    'SeedFleetCommandTests',
]
