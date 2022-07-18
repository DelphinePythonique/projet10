from django.contrib import admin

from softdesk.models import Project, Issue, Contributor

admin.site.register(Project)
admin.site.register(Issue)
admin.site.register(Contributor)
