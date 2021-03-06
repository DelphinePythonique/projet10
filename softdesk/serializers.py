from rest_framework import serializers
from rest_framework.serializers import ModelSerializer

from .models import Project, Issue, Comment, Contributor


class ProjectListSerializer(ModelSerializer):
    author = serializers.ReadOnlyField(source="author.username")

    class Meta:
        model = Project
        fields = ["id", "title", "author", "type"]

    def validate_name(self, value):
        if Project.objects.filter(name=value).exists():
            raise serializers.ValidationError("Project already exists")
        return value


class ProjectDetailSerializer(ModelSerializer):
    author = serializers.ReadOnlyField(source="author.username")
    issues = serializers.SerializerMethodField()
    contribute_by = serializers.SerializerMethodField()

    class Meta:
        model = Project
        fields = [
            "id",
            "title",
            "description",
            "author",
            "type",
            "contribute_by",
            "issues",
        ]

    def get_issues(self, instance):

        queryset = instance.issues
        serializer = IssueListSerializer(queryset, many=True)
        return serializer.data

    def get_contribute_by(self, instance):

        queryset = instance.contribute_by
        serializer = ContributorSerializer(queryset, many=True)
        return serializer.data


class ContributorSerializer(ModelSerializer):
    user = serializers.ReadOnlyField(source="user.username")

    class Meta:
        model = Contributor
        fields = ["user", "permission"]


class ContributorDetailSerializer(ModelSerializer):
    project = serializers.ReadOnlyField(source="project.title")

    class Meta:
        model = Contributor
        fields = ["project", "user", "permission"]


class IssueListSerializer(ModelSerializer):
    class Meta:
        model = Issue
        fields = [
            "id",
            "title",
            "author",
            "tag",
            "priority",
            "status",
        ]


class IssueDetailSerializer(ModelSerializer):
    project = serializers.ReadOnlyField(source="project.title")
    author = serializers.ReadOnlyField(source="author.username")
    comments = serializers.SerializerMethodField()

    class Meta:
        model = Issue
        fields = [
            "id",
            "title",
            "description",
            "tag",
            "priority",
            "status",
            "project",
            "created_time",
            "author",
            "assignee",
            "comments",
        ]

    def get_comments(self, instance):

        queryset = instance.comments
        serializer = CommentListSerializer(queryset, many=True)
        return serializer.data

    def validate_assignee(self, value):
        expected_assignee = self.context["contributors"]
        if value not in expected_assignee:
            raise serializers.ValidationError("Assignee not in contributors")
        return value


class CommentListSerializer(ModelSerializer):
    issue = serializers.ReadOnlyField(source="issue.title")
    author = serializers.ReadOnlyField(source="author.username")

    class Meta:
        model = Comment
        fields = ["id", "issue", "description", "author", "created_time"]


class CommentDetailSerializer(ModelSerializer):

    issue = serializers.ReadOnlyField(source="issue.title")
    author = serializers.ReadOnlyField(source="author.username")

    class Meta:
        model = Comment
        fields = ["id", "description", "issue", "author", "created_time"]
