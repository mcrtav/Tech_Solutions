# setup/urls.py
from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from produtos.views import ProdutoViewSets
from usuarios.views import UsuarioViewSets

# Criar apenas UM router para toda a aplicação
router = DefaultRouter()
router.register(r'usuarios', UsuarioViewSets, basename='usuarios')
router.register(r'produtos', ProdutoViewSets, basename='produtos')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include(router.urls)),
]