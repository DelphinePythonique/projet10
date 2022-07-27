from django.contrib.auth import get_user_model
from django.contrib.auth.models import User
from rest_framework.permissions import IsAuthenticated

from .serializers import RegisterSerializer
from rest_framework import generics


class RegisterView(generics.CreateAPIView):
    queryset = get_user_model().objects.all()
    permission_classes = IsAuthenticated
    serializer_class = RegisterSerializer
