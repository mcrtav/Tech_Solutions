# usuarios/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from usuarios.views import UsuarioViewSets

router = DefaultRouter()
router.register(r'usuarios', UsuarioViewSets, basename='usuario')

urlpatterns = [
    path('', include(router.urls)),
]

# Inclua as URLs do JWT se necessário
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

urlpatterns += [
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]