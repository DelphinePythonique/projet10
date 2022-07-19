from django.conf import settings
from django.db import models, transaction

CHOICE_TYPE = [
    ("BACKEND", "back-end"),
    ("FRONTEND", "front-end"),
    ("SMARTPHONE", "iOS ou Android"),
]
CHOICE_TAG = [("BUG", "bug"), ("IMPROVEMENT", "improvement"), ("TASK", "task")]
CHOICE_PRIORITY = [("LOW", "low"), ("MEDIUM", "medium"), ("HIGH", "high")]
CHOICE_STATUS = [
    ("TODO", "to do"),
    ("INPROGESS", "in progress"),
    ("FINISHED", "finished"),
]


class Project(models.Model):
    title = models.CharField(max_length=128)
    description = models.CharField(max_length=2048, blank=True)
    author = models.ForeignKey(to=settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    type = models.CharField(max_length=10, choices=CHOICE_TYPE)

    @property
    def get_all_contributor(self):
        contributors = [c.user for c in self.contribute_by.all()]
        contributors.append(self.author)
        return contributors

    def __str__(self):
        return self.title


class Issue(models.Model):
    title = models.CharField(max_length=128)
    description = models.CharField(max_length=2048, blank=True)
    tag = models.CharField(max_length=11, choices=CHOICE_TAG)
    priority = models.CharField(max_length=6, choices=CHOICE_PRIORITY)
    status = models.CharField(max_length=9, choices=CHOICE_STATUS)
    project = models.ForeignKey(
        to=Project, on_delete=models.CASCADE, related_name="issues"
    )
    created_time = models.DateTimeField(auto_now_add=True)
    author = models.ForeignKey(
        to=settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="author",
    )
    assignee = models.ForeignKey(
        to=settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="assignee",
    )

    @property
    def get_all_contributor(self):
        return self.project.get_all_contributor

    def __str__(self):
        return f"{self.project}-{self.title}"


class Comment(models.Model):
    description = models.CharField(max_length=2048, blank=True)
    author = models.ForeignKey(to=settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    issue = models.ForeignKey(to=Issue, on_delete=models.CASCADE, related_name="comments")
    created_time = models.DateTimeField(auto_now_add=True)

    @property
    def get_all_contributor(self):
        return self.issue.get_all_contributor

    def __str__(self):
        return f"{self.issue}-{self.id}"


class Contributor(models.Model):
    # Your UserFollows model definition goes here
    user = models.ForeignKey(
        to=settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="contribute_to",
    )
    project = models.ForeignKey(
        to=Project,
        on_delete=models.CASCADE,
        related_name="contribute_by",
    )
    permission = models.BooleanField()

    @property
    def get_all_contributor(self):
        return self.project.get_all_contributor

    def __str__(self):
        return f"{self.user}: contribute to project  {self.project}"

    class Meta:
        # ensures we don't get multiple UserFollows instances
        # for unique user-user_followed pairs
        unique_together = (
            "user",
            "project",
        )
