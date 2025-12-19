# usuarios/admin.py
from django.contrib import admin
from .models import Usuario

@admin.register(Usuario)
class UsuarioAdmin(admin.ModelAdmin):
    list_display = ('nome', 'email', 'telefone', 'criado')
    list_filter = ('criado',)
    search_fields = ('nome', 'email', 'telefone')
    ordering = ('nome',)
    
    fieldsets = (
        ('Informações Pessoais', {
            'fields': ('nome', 'email', 'telefone')
        }),
        ('Segurança', {
            'fields': ('senha',)
        }),
        ('Datas', {
            'fields': ('criado', 'atualizado'),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ('criado', 'atualizado')