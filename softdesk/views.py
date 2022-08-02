from django.db.models import Q

# Create your views here.
from rest_framework import status, mixins
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.schemas.openapi import AutoSchema
from rest_framework.viewsets import ReadOnlyModelViewSet, ModelViewSet, GenericViewSet

from softdesk.models import Project, Issue, Comment
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


class ProjectViewset(ModelViewSet):
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
        tags=['Project'],
        component_name='Project',
        operation_id_base='Project',
    )

    serializer_class = ProjectListSerializer
    detail_serializer_class = ProjectDetailSerializer
    add_contributor_serializer_class = ContributorDetailSerializer
    add_issue_serializer_class = IssueDetailSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        if isinstance(serializer, (ProjectListSerializer, ProjectDetailSerializer)):
            serializer.save(author=self.request.user)
        if isinstance(serializer, ContributorDetailSerializer):
            serializer.save(project=self.get_object())
        if isinstance(serializer, IssueDetailSerializer):
            serializer.save(project=self.get_object(), author=self.request.user)

    @action(detail=True, methods=["POST"])
    def add_contributor(self, request, *args, **kwargs):
        """
        post: Add a contributor to a project, only accessible to a project contributor
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(
            serializer.data, status=status.HTTP_201_CREATED, headers=headers
        )

    @action(detail=True, methods=["POST"])
    def add_issue(self, request, *args, **kwargs):
        """
        post: Add an issue to a project, only accessible to a project contributor
        """
        project = self.get_object()
        serializer_context = self.get_serializer_context()
        serializer_context["contributors"] = project.all_contributors
        serializer = self.get_serializer(data=request.data, context=serializer_context)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(
            serializer.data, status=status.HTTP_201_CREATED, headers=headers
        )

    def get_queryset(self):

        return Project.objects.filter(
            Q(author=self.request.user) | Q(contribute_by__user=self.request.user)
        ).distinct()

    def get_serializer_class(self):
        if self.action == "retrieve":
            return self.detail_serializer_class
        if self.action == "add_contributor":
            return self.add_contributor_serializer_class
        if self.action == "add_issue":
            return self.add_issue_serializer_class
        return super().get_serializer_class()

    def get_permissions(self):
        if self.action in ("update", "partial_update", "destroy"):
            self.permission_classes = [IsAuthenticated, IsOwner]
        elif self.action in ("list", "retrieve", "add_contributor", "add_issue"):
            self.permission_classes = [IsAuthenticated, IsContributor]
        else:
            self.permission_classes = [IsAuthenticated]
        return super().get_permissions()


class IssueViewset(
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    mixins.ListModelMixin,
    GenericViewSet,
):
    """
    list:
    Return the list of issues linked to project to which the authenticated user contributes.

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
        tags=['project', 'issue'],
        component_name='Issue',
        operation_id_base='Issue',
    )

    serializer_class = IssueListSerializer
    detail_serializer_class = IssueDetailSerializer
    add_comment_serializer_class = CommentDetailSerializer
    permission_classes = [IsAuthenticated]

    @action(detail=True, methods=["POST"])
    def add_comment(self, request, *args, **kwargs):
        """
        post: Add a comment to an issue, only accessible to a project contributor
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(issue=self.get_object(), author=self.request.user)

        return Response(
            serializer.data, status=status.HTTP_201_CREATED
        )


    def get_serializer_class(self):
        if self.action == "retrieve":
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

        return Issue.objects.filter(
            Q(author=self.request.user)
            | Q(project__contribute_by__user=self.request.user)
            | Q(project__author=self.request.user)
        ).distinct()


class CommentViewset(
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    mixins.ListModelMixin,
    GenericViewSet,
):

    """
    list:
    Returns the list of comments linked to project which the authenticated user contributes.

    retrieve:
    Return a comment linked to project which the authenticated user contributes.

    update:
    update a comment, only accessible to comment's author

    partial_update:
    update an issue, only accessible to comment's author

    destroy:
    delete an issue, only accessible to comment's author

    """

    schema = AutoSchema(
        tags=['project', 'issue', 'comment'],
        component_name='Comment',
        operation_id_base='Comment',
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

        return Comment.objects.filter(
            Q(author=self.request.user)
            | Q(issue__project__contribute_by__user=self.request.user)
            | Q(issue__project__author=self.request.user)
        ).distinct()
