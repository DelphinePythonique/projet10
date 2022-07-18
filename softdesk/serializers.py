from rest_framework import serializers
from rest_framework.serializers import ModelSerializer

from .models import Project, Issue, Comment, Contributor


class ProjectListSerializer(ModelSerializer):
    author = serializers.ReadOnlyField(source='author.username')

    class Meta:
        model = Project
        fields = ["id", "title", "author", "type"]

    def validate_name(self, value):
        if Project.objects.filter(name=value).exists():
            raise serializers.ValidationError('Project already exists')
        return value


class ProjectDetailSerializer(ModelSerializer):
    author = serializers.ReadOnlyField(source='author.username')
    issues = serializers.SerializerMethodField()
    contribute_by = serializers.SerializerMethodField()

    class Meta:
        model = Project
        fields = ["id", "title", "description", "author", "type", "contribute_by", "issues"]

    def get_issues(self, instance):

        queryset = instance.issues
        serializer = IssueListSerializer(queryset, many=True)
        return serializer.data

    def get_contribute_by(self, instance):

        queryset = instance.contribute_by
        serializer = ContributorSerializer(queryset, many=True)
        return serializer.data


class ContributorSerializer(ModelSerializer):
    user = serializers.ReadOnlyField(source='user.username')

    class Meta:
        model = Contributor
        fields = ["user", "permission"]


class ContributorDetailSerializer(ModelSerializer):
    project = serializers.ReadOnlyField(source='project.title')

    class Meta:
        model = Contributor
        fields = ["project", "user", "permission"]


class IssueListSerializer(ModelSerializer):
    class Meta:
        model = Issue
        fields = [
            "title",
            "author",
            "tag",
            "priority",
            "status",
         ]


class IssueDetailSerializer(ModelSerializer):
    project = serializers.ReadOnlyField(source='project.title')
    author = serializers.ReadOnlyField(source='author.username')

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
        ]


class CommentSerializer(ModelSerializer):
    class Meta:
        model = Comment
        fields = ["id", "description", "author", "created_time"]
