from django.shortcuts import render
from django.core.exceptions import PermissionDenied


def permission_denied_view(request, exception):
    return render(request, "errors/403.html", status=403)
