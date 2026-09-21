from django.conf import settings


def fleet_features(request):
    """Expose application feature toggles to all templates."""
    return {
        'ENABLE_AI_COPILOT': getattr(settings, 'ENABLE_AI_COPILOT', False),
    }
