from django.shortcuts import render


def bad_request_view(request, exception=None):
    """Custom HTTP 400 Bad Request handler."""
    return render(request, '400.html', status=400)


def permission_denied_view(request, exception=None):
    """Custom HTTP 403 Forbidden handler."""
    return render(request, '403.html', status=403)


def page_not_found_view(request, exception=None):
    """Custom HTTP 404 Not Found handler."""
    return render(request, '404.html', status=404)


def server_error_view(request):
    """Custom HTTP 500 Internal Server Error handler."""
    return render(request, '500.html', status=500)
