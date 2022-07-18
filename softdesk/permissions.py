from rest_framework.permissions import BasePermission, SAFE_METHODS

from softdesk.models import Project, Issue, Contributor


class IsOwnerOrReadOnly(BasePermission):
    """
    Custom permission to only allow owners of an object to edit it.
    """

    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request,
        # so we'll always allow GET, HEAD or OPTIONS requests.
        if request.method in SAFE_METHODS:
            return True

        # Write permissions are only allowed to the owner of the snippet.
        if isinstance(obj, (Project, Issue)):
            if view.action == 'addIssue':
                object.project.author = request.user
            else:
                return obj.author == request.user
        elif isinstance(obj, Contributor):
            return obj.project.author == request.user
        else:
            return False



