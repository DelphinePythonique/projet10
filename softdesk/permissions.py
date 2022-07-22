from rest_framework.permissions import BasePermission, SAFE_METHODS

from softdesk.models import Project, Issue, Contributor, Comment


class IsOwner(BasePermission):
    """
    Custom permission to only allow owners of an object to create it.
    """

    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request,
        # so we'll always allow GET, HEAD or OPTIONS requests.
        #if request.method in SAFE_METHODS:
        #    return True
        return obj.author == request.user

class IsContributor(BasePermission):

    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request,
        # so we'll always allow GET, HEAD or OPTIONS requests.
        # if request.method in SAFE_METHODS:
        #    return True
        return request.user in obj.all_contributors