from django.shortcuts import render
from django.urls import resolve

from base_app.models import MaintenanceDataStore


class MaintenanceMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        # One-time configuration and initialization.

    def __call__(self, request):
        # Code to be executed for each request before
        # the view (and later middleware) are called.

        maintenance_object, _ = MaintenanceDataStore.objects.get_or_create(id=1)
        if (
            maintenance_object.status == MaintenanceDataStore.IS_UNDER_MAINTENANCE
            and resolve(request.path_info).url_name != "maintenance"
        ):
            return render(request, "maintenance.html")
        response = self.get_response(request)

        # Code to be executed for each request/response after
        # the view is called.

        return response
