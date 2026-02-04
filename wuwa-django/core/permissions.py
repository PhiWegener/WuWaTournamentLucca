from functools import wraps
from django.http import HttpResponseForbidden
from django.shortcuts import redirect

def requireLogin(viewFunc):
    @wraps(viewFunc)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect("login")
        return viewFunc(request, *args, **kwargs)
    return wrapper

def requireRole(*allowedRoles):
    def decorator(viewFunc):
        @wraps(viewFunc)
        def wrapper(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return redirect("login")
            if request.user.role not in allowedRoles:
                return HttpResponseForbidden("Forbidden")
            return viewFunc(request, *args, **kwargs)
        return wrapper
    return decorator
