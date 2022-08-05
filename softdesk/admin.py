from django.contrib import admin

from softdesk.models import Project, Issue, Contributor, Comment


class IssueAdmin(admin.ModelAdmin):
    list_display = ('title', 'project')

admin.site.register(Project)
admin.site.register(Issue, IssueAdmin)
admin.site.register(Contributor)
admin.site.register(Comment)
