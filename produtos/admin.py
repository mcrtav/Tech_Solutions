# produtos/admin.py
from django.contrib import admin
from .models import Produto

@admin.register(Produto)
class ProdutoAdmin(admin.ModelAdmin):
    list_display = ('nome', 'marca', 'preco', 'criado')
    list_filter = ('marca', 'criado')
    search_fields = ('nome', 'marca', 'descricao')
    ordering = ('nome',)