from .test_admin import FleetAdminTests
from .test_agent import AIAgentAndActionsTestCase
from .test_auth import AuthenticationAndTelematicsTests
from .test_commands import SeedFleetCommandTests
from .test_localization import LocalizationIntegrationTests
from .test_models import MaintenanceScheduleModelTests, TripLogModelTests, VehicleModelTests
from .test_queue_and_errors import QueueAndErrorHandlersTestCase
from .test_views import OperationsPagesTests

__all__ = [
    'VehicleModelTests',
    'TripLogModelTests',
    'MaintenanceScheduleModelTests',
    'OperationsPagesTests',
    'AuthenticationAndTelematicsTests',
    'LocalizationIntegrationTests',
    'FleetAdminTests',
    'SeedFleetCommandTests',
    'AIAgentAndActionsTestCase',
    'QueueAndErrorHandlersTestCase',
]
