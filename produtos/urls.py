# produtos/urls.py
from django.urls import path
from produtos import views

urlpatterns = [
    path('produtos/', views.ProdutoViewSets.as_view({
        'get': 'list',
        'post': 'create'
    }), name='produto-list'),
    
    path('produtos/<int:pk>/', views.ProdutoViewSets.as_view({
        'get': 'retrieve',
        'put': 'update',
        'patch': 'partial_update',
        'delete': 'destroy'
    }), name='produto-detail'),
    
    path('produtos/buscar/', views.ProdutoViewSets.as_view({
        'get': 'buscar'
    }), name='produto-buscar'),
]