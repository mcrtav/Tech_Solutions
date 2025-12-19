from rest_framework_simplejwt.authentication import JWTAuthentication

# autenticação original,
# isso vc vai herdar e modificar
from rest_framework.exceptions import AuthenticationFailed

# se der errado: lança exceção
# (usuario não existe || token invalido)

from .models import Usuario

# Ideia: Criar uma nova versão de autenticação
# baseada no JWT

# Pq? -> A classe JWTAuthentication assume que os
# usuários estão na tabela padrão do Django (auth)

# Então... Temos que sobrescrever essa parte da
# logica para que o SimpleJWT olha na nossa tabela


class CustomJWTAuthentication(JWTAuthentication):
    """
    Herda o comportamento padrão e modifica apenas
    o necessario
    """

    def get_user(self, validated_data):
        """
        Sobrescreve o metodo padrão get_user
        Agora busca na tabela 'usuarios' ao inves da
        tabela 'auth_user'
        Retorna o usuario correspondente ao token
        """
        try:
            user_id = validated_data["user_id"]

            # buscar na tabela de usuarios
            usuario = Usuario.objects.get(id=user_id)
            return usuario
        except Usuario.DoesNotExist:
            raise AuthenticationFailed("Usuario não encontrado", code="user_not_found")
        except KeyError:
            raise AuthenticationFailed("Token Inválido", code="token_invalid")
