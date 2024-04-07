from rest_framework import status
from rest_framework.permissions import (
    BasePermission,
    SAFE_METHODS,
)  # ('GET', 'HEAD', 'OPTIONS')
from rest_framework.exceptions import APIException


class Is_Owner_or_Admin(BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True
        return obj.owner == request.user or request.user.is_staff or request.user.is_superuser

