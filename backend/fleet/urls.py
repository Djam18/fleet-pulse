from django.urls import path

from . import views

app_name = 'fleet'

urlpatterns = [
    # Core Fleet Management Pages
    path('', views.dashboard_view, name='dashboard'),
    path('vehicles/', views.vehicle_list_view, name='vehicle_list'),
    path('vehicles/<int:pk>/', views.vehicle_detail_view, name='vehicle_detail'),
    path('trips/', views.trip_list_view, name='trip_list'),
    path('maintenance/', views.maintenance_list_view, name='maintenance_list'),
    path('inspections/', views.inspection_list_view, name='inspection_list'),

    # Real-time Telematics SSE Stream
    path('telematics/stream/', views.telematics_stream_view, name='telematics_stream'),

    # AI Fleet Copilot & Autonomous Agent Action Endpoints
    path('api/ai/chat/', views.ai_chat_view, name='ai_chat'),
    path('actions/status-request/', views.status_request_create_view, name='status_request_create'),
    path('actions/quick-trip/', views.quick_trip_create_view, name='quick_trip_create'),
    path('actions/notifications/<int:pk>/read/', views.mark_notification_read_view, name='mark_notification_read'),

    # Non-Admin User Authentication (Mailpit integration)
    path('login/', views.FleetLoginView.as_view(), name='login'),
    path('logout/', views.FleetLogoutView.as_view(), name='logout'),
    path('register/', views.FleetRegisterView.as_view(), name='register'),
    path('password-reset/', views.FleetPasswordResetView.as_view(), name='password_reset'),
    path('password-reset/done/', views.FleetPasswordResetDoneView.as_view(), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', views.FleetPasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('reset/done/', views.FleetPasswordResetCompleteView.as_view(), name='password_reset_complete'),
]
