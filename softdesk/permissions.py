from rest_framework.permissions import BasePermission, SAFE_METHODS

from softdesk.models import Project, Issue, Contributor, Comment


class IsOwnerOrReadOnly(BasePermission):
    """
    Custom permission to only allow owners of an object to edit it.
    """

    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request,
        # so we'll always allow GET, HEAD or OPTIONS requests.
        if request.method in SAFE_METHODS:
            return True
        who_is_owner = {
            Project: {
                "create": True,
                "update": "author",
                "partial_update": "author",
                "destroy": "author",
                "addIssue": "get_all_contributor",
                "addContributor": "get_all_contributor",
            },
            Contributor: {
                "addContributor": "get_all_contributor",
            },
            Issue: {
                "addIssue": "get_all_contributor",
                "addComment": "get_all_contributor",
                "update": "author",
                "partial_update": "author",
                "destroy": "author",
            },
            Comment: {
                "addComment": "get_all_contributor",
                "update": "author",
                "partial_update": "author",
                "destroy": "author",
            },
        }

        if who_is_owner[type(obj)][view.action] == True:
            return True

        print(f" qui est proprio : {who_is_owner[type(obj)][view.action]}")
        authorized_users = getattr(obj, who_is_owner[type(obj)][view.action])

        if not isinstance(authorized_users, list):
            return request.user == authorized_users
        if isinstance(authorized_users, list):
            return request.user in authorized_users

        return False
