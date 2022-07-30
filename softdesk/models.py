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


def get_help_text(calling_class, choices):
    text = [f"This field is used to categorize the {calling_class}. Use"]
    text.extend([f"{choice[0]}=>{choice[1]}" for choice in choices])
    return ', '.join(text)


class Project(models.Model):
    title = models.CharField(max_length=128, help_text="project's title")
    description = models.CharField(max_length=2048, blank=True,  help_text="project's description")
    author = models.ForeignKey(to=settings.AUTH_USER_MODEL, on_delete=models.CASCADE, help_text="project's author")
    type = models.CharField(max_length=10, choices=CHOICE_TYPE, help_text=get_help_text("project", CHOICE_TYPE))

    @property
    def all_contributors(self):
        contributors = [c.user for c in self.contribute_by.all()]
        contributors.append(self.author)
        return contributors

    @property
    def all_contributor_ids(self):
        contributor_ids = [c.user.id for c in self.contribute_by.all()]
        contributor_ids.append(self.author.id)
        return contributor_ids

    def __str__(self):
        return self.title


class Issue(models.Model):
    title = models.CharField(max_length=128)
    description = models.CharField(max_length=2048, blank=True)
    tag = models.CharField(max_length=11, choices=CHOICE_TAG, help_text=get_help_text("issue", CHOICE_TAG))
    priority = models.CharField(max_length=6, choices=CHOICE_PRIORITY, help_text=get_help_text("issue", CHOICE_PRIORITY))
    status = models.CharField(max_length=9, choices=CHOICE_STATUS, help_text=get_help_text("issue", CHOICE_STATUS))
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
    def all_contributors(self):
        return self.project.all_contributors

    @property
    def all_contributor_ids(self):
        return self.project.all_contributor_ids

    def __str__(self):
        return f"{self.project}-{self.title}"


class Comment(models.Model):
    description = models.CharField(max_length=2048, blank=True)
    author = models.ForeignKey(to=settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    issue = models.ForeignKey(to=Issue, on_delete=models.CASCADE, related_name="comments")
    created_time = models.DateTimeField(auto_now_add=True)

    @property
    def all_contributors(self):
        return self.issue.all_contributors

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
    def all_contributors(self):
        return self.project.all_contributors

    def __str__(self):
        return f"{self.user}: contribute to project  {self.project}"

    class Meta:
        # ensures we don't get multiple UserFollows instances
        # for unique user-user_followed pairs
        unique_together = (
            "user",
            "project",
        )
