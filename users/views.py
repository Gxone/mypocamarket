from rest_framework.mixins import ListModelMixin
from rest_framework.viewsets import GenericViewSet

from users.models import User
from users.serializers import UserSerializer


class UsersViewSet(ListModelMixin, GenericViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
