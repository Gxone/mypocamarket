from django.urls import path, include
from rest_framework.routers import DefaultRouter

from sales.views import SaleViewSet
from users.views import UsersViewSet

router = DefaultRouter()
router.register(r'sales', SaleViewSet, basename='sales')
router.register(r'users', UsersViewSet, basename='users')

urlpatterns = [
    path('', include(router.urls)),
]
