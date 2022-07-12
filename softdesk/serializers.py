from rest_framework import serializers
from rest_framework.serializers import ModelSerializer

from .models import Project, Issue, Comment


class ProjectListSerializer(ModelSerializer):

    class Meta:
        model = Project
        fields = ["id", "title", "user", "type", "issues"]

    def validate_name(self, value):
        if Project.objects.filter(name=value).exists():
            raise serializers.ValidationError('Project already exists')
        return value

    """
    def validate(self, data):
        # Effectuons le contrôle sur la présence du nom dans la description
        if data['name'] not in data['description']:
            # Levons une ValidationError si ça n'est pas le cas
            raise serializers.ValidationError('Name must be in description')
        return data
    """

class ProjectDetailSerializer(ModelSerializer):

    issues = serializers.SerializerMethodField()

    class Meta:
        model = Project
        fields = ["id", "title", "description", "user", "type", "issues"]

    def get_issues(self, instance):

        queryset = instance.issues
        serializer = IssueSerializer(queryset, many=True)
        return serializer.data


class IssueSerializer(ModelSerializer):
    class Meta:
        model = Issue
        fields = [
            "id",
            "title",
            "description",
            "user",
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
