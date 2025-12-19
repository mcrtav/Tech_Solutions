# importar views e o router
from rest_framework.routers import DefaultRouter
# router é responsavel por gerar automaticamente
# todas as rotas REST

# ATENÇÃO TUDO QUE É USUARIO VIRA PRODUTO
from usuarios import views

# criar uma instancia (objeto) do router
# Obs.: DefaultRouter ja gera a rota para
# a interface de navegação do DRF
router = DefaultRouter()

# registrar o ViewSet no router
# função register que tem 3 parametros
# 1º -> prefixo da rota ('usuarios/')
# 2º -> classe do ViewSet
# 3º -> nome base (nome interno usado pelo DRF)
# esse nome base evita conflitos
router.register(
	r'usuarios', # qualquer caracter é reconhecido
	# como caracter normal (mesmo sendo especial)
	views.UsuarioViewSets, # controla as rotas
	basename='usuarios'
)
# criar as rotas automaticamente
urlpatterns = router.urls