"""project URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from rest_framework import routers
from rest_framework_extensions.routers import ExtendedSimpleRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from authentication.views import RegisterView
from softdesk.views import (
    ProjectViewset,
    IssueViewset,
    CommentViewset,
    ContributorViewset,
)

router = ExtendedSimpleRouter()
(
    router.register("project", ProjectViewset, basename="project")
    .register(
        "issue",
        IssueViewset,
        basename="project-issue",
        parents_query_lookups=["project"],
    )
    .register(
        "comment",
        CommentViewset,
        basename="project-issue-comment",
        parents_query_lookups=["issue__project", "issue"],
    ),
    router.register("project", ProjectViewset, basename="project").register(
        "user",
        ContributorViewset,
        basename="project-user",
        parents_query_lookups=["project"],
    ),
)
urlpatterns = [
    path("admin/", admin.site.urls),
    path("api-auth/", include("rest_framework.urls")),
    path("api/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("api/login/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("api/signup/", RegisterView.as_view(), name="signup"),
    path("api/", include(router.urls)),
]
