from django.contrib.auth.decorators import login_required
from django.http import StreamingHttpResponse

from fleet.services.ai_agent import run_local_agent_stream


@login_required
def ai_chat_view(request):
    """
    Streaming Server-Sent Events (SSE) view powering the conversational
    FleetPulse AI Copilot and autonomous operations agent.
    """
    prompt = request.GET.get('prompt') or request.POST.get('prompt', '')
    if not prompt:
        prompt = "Bonjour"

    response = StreamingHttpResponse(
        run_local_agent_stream(prompt, request.user),
        content_type='text/event-stream'
    )
    response['Cache-Control'] = 'no-cache, no-transform'
    response['X-Accel-Buffering'] = 'no'
    return response
