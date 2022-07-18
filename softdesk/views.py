from django.db.models import Q
from django.shortcuts import render

# Create your views here.
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ReadOnlyModelViewSet, ModelViewSet

from softdesk.models import Project, Issue
from softdesk.permissions import IsOwnerOrReadOnly
from softdesk.serializers import ProjectListSerializer, ProjectDetailSerializer, ContributorDetailSerializer, \
    IssueDetailSerializer, IssueListSerializer


class ProjectViewset(ReadOnlyModelViewSet):
    serializer_class = ProjectListSerializer
    detail_serializer_class = ProjectDetailSerializer
    permission_classes = [IsAuthenticated]
    def get_queryset(self):

        return Project.objects.filter(Q(author=self.request.user) | Q(contribute_by__user=self.request.user))

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return self.detail_serializer_class
        return super().get_serializer_class()


class AdminProjectViewset(ModelViewSet):
    serializer_class = ProjectListSerializer
    detail_serializer_class = ProjectDetailSerializer
    add_contributor_serializer_class = ContributorDetailSerializer
    add_issue_serializer_class = IssueDetailSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrReadOnly]

    def perform_create(self, serializer):
        if isinstance(serializer, (ProjectListSerializer, ProjectDetailSerializer)):
            serializer.save(author=self.request.user)
        if isinstance(serializer, ContributorDetailSerializer):
            serializer.save(project=self.get_object())
        if isinstance(serializer, IssueDetailSerializer):
            serializer.save(project=self.get_object(), author=self.request.user)

    @action(detail=True, methods=['POST'], url_path="add_contributor")
    def addContributor(self, request, *args, **kwargs):

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    @action(detail=True, methods=['POST'], url_path="add_issue")
    def addIssue(self, request, *args, **kwargs):

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def get_queryset(self):
        return Project.objects.filter(Q(author=self.request.user)| Q(contribute_by__user=self.request.user))

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return self.detail_serializer_class
        if self.action == 'addContributor':
            return self.add_contributor_serializer_class
        if self.action == 'addIssue':
            return self.add_issue_serializer_class
        return super().get_serializer_class()


class AdminIssueViewset(ModelViewSet):
    serializer_class = IssueListSerializer
    detail_serializer_class = IssueDetailSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrReadOnly]

    def perform_update(self, serializer):
        pass

    def get_queryset(self):
        return Issue.objects.filter(Q(author=self.request.user)| Q(project__contribute_by__user=self.request.user))

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return self.detail_serializer_class
        return super().get_serializer_class()
