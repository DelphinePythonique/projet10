from django.db.models import Q

# Create your views here.
from rest_framework import mixins
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.schemas.openapi import AutoSchema
from rest_framework.viewsets import ModelViewSet, GenericViewSet
from rest_framework_extensions.mixins import NestedViewSetMixin

from softdesk.models import Project, Issue, Comment, Contributor
from softdesk.permissions import IsOwner, IsContributor
from softdesk.serializers import (
    ProjectListSerializer,
    ProjectDetailSerializer,
    ContributorDetailSerializer,
    IssueDetailSerializer,
    IssueListSerializer,
    CommentListSerializer,
    CommentDetailSerializer,
)


class ProjectViewset(NestedViewSetMixin, ModelViewSet):
    """
    list:
    Returns the list of projects to which the authenticated user contributes.

    create:
    create a project instance, only accessible to an authenticated user.

    retrieve:
    Return a project instance.

    update:
    update a project instance, only accessible to project's author

    partial_update:
    update a project instance, only accessible to project's author

    destroy:
    delete a project, only accessible to project's author

    """

    schema = AutoSchema(
        tags=["Project"],
        component_name="Project",
        operation_id_base="Project",
    )

    serializer_class = ProjectListSerializer
    detail_serializer_class = ProjectDetailSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def get_queryset(self):

        return Project.objects.filter(
            Q(author=self.request.user) | Q(contribute_by__user=self.request.user)
        ).distinct()

    def get_permissions(self):
        if self.action in ("update", "partial_update", "destroy"):
            self.permission_classes = [IsAuthenticated, IsOwner]
        elif self.action in ("list", "retrieve", "add_contributor", "add_issue"):
            self.permission_classes = [IsAuthenticated, IsContributor]
        else:
            self.permission_classes = [IsAuthenticated]
        return super().get_permissions()


class IssueViewset(NestedViewSetMixin, ModelViewSet):
    """
    list:
    Return the list of issues linked to project to which the authenticated user contributes.

    create:
    create an issue linked to project to which the authenticated user contributes.

    retrieve:
    Return an issue linked to project to which the authenticated user contributes.

    update:
    update an issue, only accessible to issue's author

    partial_update:
    update an issue, only accessible to issue's author

    destroy:
    delete an issue, only accessible to issue's author

    """

    schema = AutoSchema(
        tags=["project", "issue"],
        component_name="Issue",
        operation_id_base="Issue",
    )

    serializer_class = IssueListSerializer
    detail_serializer_class = IssueDetailSerializer
    add_comment_serializer_class = CommentDetailSerializer
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.action in ("retrieve", "partial_update", "update"):
            return self.detail_serializer_class
        if self.action == "add_comment":
            return self.add_comment_serializer_class
        return super().get_serializer_class()

    def get_permissions(self):
        if self.action in ("update", "partial_update", "destroy"):
            self.permission_classes = [IsAuthenticated, IsOwner]
        elif self.action in ("list", "retrieve", "add_comment"):
            self.permission_classes = [IsAuthenticated, IsContributor]
        else:
            self.permission_classes = [IsAuthenticated]
        return super().get_permissions()

    def get_queryset(self):
        project = Project.objects.get(pk=self.kwargs["parent_lookup_project"])
        return (
            Issue.objects.filter(project=project)
            .filter(
                Q(author=self.request.user)
                | Q(project__contribute_by__user=self.request.user)
                | Q(project__author=self.request.user)
            )
            .distinct()
        )

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop("partial", False)
        instance = self.get_object()

        serializer_context = self.get_serializer_context()
        serializer_context["contributors"] = instance.all_contributors

        serializer = self.get_serializer(
            instance, data=request.data, partial=partial, context=serializer_context
        )
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        if getattr(instance, "_prefetched_objects_cache", None):
            # If 'prefetch_related' has been applied to a queryset, we need to
            # forcibly invalidate the prefetch cache on the instance.
            instance._prefetched_objects_cache = {}

        return Response(serializer.data)

    def create(self, request, *args, **kwargs):
        project = Project.objects.get(pk=self.kwargs["parent_lookup_project"])
        serializer_context = self.get_serializer_context()
        serializer_context["contributors"] = project.all_contributors

        serializer = self.get_serializer(data=request.data, context=serializer_context)
        serializer.is_valid(raise_exception=True)
        serializer.save(project=project, author=self.request.user)

        return Response(serializer.data)


class ContributorViewset(
    NestedViewSetMixin,
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.DestroyModelMixin,
    mixins.ListModelMixin,
    GenericViewSet,
):
    """
    list:
    Return the list of contributors linked to project

    create:
    add a contributor linked to project to which the authenticated user contributes.

    retrieve:
    Return a contributor linked to project to which the authenticated user contributes .


    destroy:
    delete a contributor

    """

    schema = AutoSchema(
        tags=["project", "contributor"],
        component_name="Contributor",
        operation_id_base="Contributor",
    )

    serializer_class = ContributorDetailSerializer
    detail_serializer_class = ContributorDetailSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        project = Project.objects.get(pk=self.kwargs["parent_lookup_project"])
        return Contributor.objects.filter(project=project)

    def create(self, request, *args, **kwargs):
        project = Project.objects.get(pk=self.kwargs["parent_lookup_project"])
        serializer_context = self.get_serializer_context()
        serializer_context["contributors"] = project.all_contributors

        serializer = self.get_serializer(data=request.data, context=serializer_context)
        serializer.is_valid(raise_exception=True)
        serializer.save(project=project)
        return Response(serializer.data)


class CommentViewset(NestedViewSetMixin, ModelViewSet):

    """
    list:
    Returns the list of comments linked to project which the authenticated user contributes.

    create:
    create a comment linked to project's issue which the authenticated user contributes.

    retrieve:
    Return a comment linked to project's issue which the authenticated user contributes.

    update:
    update a comment, only accessible to comment's author

    partial_update:
    update an issue, only accessible to comment's author

    destroy:
    delete an issue, only accessible to comment's author

    """

    schema = AutoSchema(
        tags=["project", "issue", "comment"],
        component_name="Comment",
        operation_id_base="Comment",
    )
    serializer_class = CommentListSerializer
    detail_serializer_class = CommentDetailSerializer
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.action == "retrieve":
            return self.detail_serializer_class
        return super().get_serializer_class()

    def get_permissions(self):
        if self.action in ("update", "partial_update", "destroy"):
            self.permission_classes = [IsAuthenticated, IsOwner]
        elif self.action in ("list", "retrieve"):
            self.permission_classes = [IsAuthenticated, IsContributor]
        else:
            self.permission_classes = [IsAuthenticated]
        return super().get_permissions()

    def get_queryset(self):
        issue = Issue.objects.get(pk=self.kwargs["parent_lookup_issue"])
        return (
            Comment.objects.filter(issue=issue)
            .filter(
                Q(author=self.request.user)
                | Q(issue__project__contribute_by__user=self.request.user)
                | Q(issue__project__author=self.request.user)
            )
            .distinct()
        )

    def create(self, request, *args, **kwargs):
        issue = Issue.objects.get(pk=self.kwargs["parent_lookup_issue"])
        serializer_context = self.get_serializer_context()
        serializer_context["contributors"] = issue.all_contributors

        serializer = self.get_serializer(data=request.data, context=serializer_context)
        serializer.is_valid(raise_exception=True)
        serializer.save(issue=issue, author=self.request.user)

        return Response(serializer.data)
