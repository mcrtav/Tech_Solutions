# usuarios/views.py - VERSÃO COMPLETA E CORRIGIDA
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError

from usuarios.models import Usuario
from usuarios.serializers import (
    UsuarioSerializer,
    LoginSerializer,
    CadastroSerializer,
    LoginResponseSerializer,
    AlterarSenhaSerializer,
    EsqueciSenhaSerializer,
    ValidarTokenSerializer,
    RedefinirSenhaSerializer
)

class UsuarioViewSets(viewsets.ModelViewSet):
    """
    ViewSet para gerenciamento completo de usuários
    
    Endpoints disponíveis:
    - GET /usuarios/ - Lista usuários (público)
    - GET /usuarios/{id}/ - Detalhes do usuário (público)
    - POST /usuarios/cadastro/ - Cadastro de novo usuário (público)
    - POST /usuarios/login/ - Login (público)
    - POST /usuarios/refresh/ - Refresh token (público)
    - GET /usuarios/perfil/ - Perfil do usuário logado (privado)
    - PATCH /usuarios/{id}/ - Atualização parcial (apenas próprio perfil)
    - DELETE /usuarios/{id}/ - Exclusão (apenas próprio perfil)
    - POST /usuarios/esqueci-senha/ - Recuperação de senha (público)
    - POST /usuarios/validar-token/ - Validação de token (público)
    - POST /usuarios/redefinir-senha/ - Redefinição de senha (público)
    - POST /usuarios/{id}/alterar-senha/ - Alteração de senha (privado, apenas próprio)
    """
    
    # QUERYSET OBRIGATÓRIO para ModelViewSet
    queryset = Usuario.objects.all().order_by('nome')
    serializer_class = UsuarioSerializer
    
    def get_permissions(self):
        '''
        Define permissões por action
        '''
        # Actions públicas
        public_actions = [
            'cadastro', 'login', 'esqueci_senha', 'validar_token',
            'redefinir_senha', 'refresh_token', 'list', 'retrieve'
        ]
        
        if self.action in public_actions:
            permission_classes = [AllowAny]
        else:
            permission_classes = [IsAuthenticated]
        
        return [permission() for permission in permission_classes]
    
    # ========== ACTIONS PÚBLICAS ==========
    
    @action(detail=False, methods=['post'],
            url_path='cadastro', 
            serializer_class=CadastroSerializer)
    def cadastro(self, request):
        """
        POST /usuarios/cadastro/
        Cadastro de novo usuário
        """
        serializer = CadastroSerializer(data=request.data)
        
        if serializer.is_valid():
            usuario = serializer.save()
            return Response(
                {
                    'mensagem': 'Usuário cadastrado com sucesso',
                    'usuario': UsuarioSerializer(usuario).data
                }, 
                status=status.HTTP_201_CREATED
            )
        
        return Response({
            'erro': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['post'],
            url_path='login',
            serializer_class=LoginSerializer)
    def login(self, request):
        """
        POST /usuarios/login/
        Login de usuário
        """
        serializer = LoginSerializer(data=request.data)
        
        if serializer.is_valid():
            usuario = serializer.validated_data['usuario']
            
            # Criar tokens JWT
            refresh = RefreshToken.for_user(usuario)
            access = refresh.access_token
            
            return Response({
                'mensagem': 'Login realizado com sucesso',
                'usuario': UsuarioSerializer(usuario).data,
                'access': str(access),
                'refresh': str(refresh)
            }, status=status.HTTP_200_OK)
        
        return Response({
            'erro': serializer.errors
        }, status=status.HTTP_401_UNAUTHORIZED)
    
    @action(detail=False, methods=['post'],
            url_path='refresh', 
            permission_classes=[AllowAny])
    def refresh_token(self, request):
        """
        POST /usuarios/refresh/
        Gera novo token de acesso usando refresh token
        """
        refresh_token = request.data.get('refresh')
        
        if not refresh_token:
            return Response({
                'erro': 'Refresh Token é obrigatório'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            refresh = RefreshToken(refresh_token)
            user_id = refresh['user_id']
            
            usuario = Usuario.objects.get(id=user_id)
            
            # Gerar novo token de acesso
            from rest_framework_simplejwt.tokens import AccessToken
            new_token_access = AccessToken.for_user(usuario)
            
            return Response({
                'access': str(new_token_access)
            }, status=status.HTTP_200_OK)
            
        except TokenError:
            return Response({
                'erro': 'Token inválido ou expirado'
            }, status=status.HTTP_401_UNAUTHORIZED)
        except Usuario.DoesNotExist:
            return Response({
                'erro': 'Usuário não encontrado'
            }, status=status.HTTP_404_NOT_FOUND)
  
    # ========== RECUPERAÇÃO DE SENHA ==========
    
    @action(detail=False, methods=['post'],
            url_path='esqueci-senha',
            permission_classes=[AllowAny],
            serializer_class=EsqueciSenhaSerializer)
    def esqueci_senha(self, request):
        """
        POST /usuarios/esqueci-senha/
        Solicita recuperação de senha por e-mail
        """
        serializer = EsqueciSenhaSerializer(data=request.data)
        
        if serializer.is_valid():
            email = serializer.validated_data['email']
            
            try:
                usuario = Usuario.objects.get(email=email)
                
                # Gerar token de recuperação
                token = usuario.gerar_token_recuperacao()
                
                # EM PRODUÇÃO: Enviar e-mail com o token
                # enviar_email_recuperacao(usuario.email, token, usuario.nome)
                
                return Response({
                    'mensagem': 'Se o e-mail estiver cadastrado, você receberá um link de recuperação',
                    'email': usuario.email,
                    'token': token,  # REMOVA EM PRODUÇÃO
                    'instrucao': 'Em produção, este token seria enviado por e-mail'
                }, status=status.HTTP_200_OK)
                
            except Usuario.DoesNotExist:
                # Por segurança, não revelamos se o e-mail existe
                return Response({
                    'mensagem': 'Se o e-mail estiver cadastrado, você receberá um link de recuperação'
                }, status=status.HTTP_200_OK)
        
        return Response({
            'erro': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['post'],
            url_path='validar-token',
            permission_classes=[AllowAny],
            serializer_class=ValidarTokenSerializer)
    def validar_token(self, request):
        """
        POST /usuarios/validar-token/
        Valida token de recuperação
        """
        serializer = ValidarTokenSerializer(data=request.data)
        
        if serializer.is_valid():
            usuario = serializer.validated_data['usuario']
            
            return Response({
                'mensagem': 'Token válido',
                'email': usuario.email,
                'nome': usuario.nome
            }, status=status.HTTP_200_OK)
        
        return Response({
            'erro': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['post'],
            url_path='redefinir-senha',
            permission_classes=[AllowAny],
            serializer_class=RedefinirSenhaSerializer)
    def redefinir_senha(self, request):
        """
        POST /usuarios/redefinir-senha/
        Redefine senha usando token de recuperação
        """
        serializer = RedefinirSenhaSerializer(data=request.data)
        
        if serializer.is_valid():
            usuario = serializer.validated_data['usuario']
            nova_senha = serializer.validated_data['nova_senha']
            
            # Atualizar senha
            usuario.senha = nova_senha
            usuario.save()
            
            # Limpar token de recuperação
            usuario.limpar_token_recuperacao()
            
            # Gerar novos tokens JWT
            refresh = RefreshToken.for_user(usuario)
            access = refresh.access_token
            
            return Response({
                'mensagem': 'Senha redefinida com sucesso',
                'usuario': UsuarioSerializer(usuario).data,
                'access': str(access),
                'refresh': str(refresh)
            }, status=status.HTTP_200_OK)
        
        return Response({
            'erro': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)
    
    # ========== ACTIONS PRIVADAS ==========
        
        # views.py - método perfil corrigido
    @action(detail=False, methods=['get'],
            url_path='perfil',
            permission_classes=[IsAuthenticated])
    def perfil(self, request):
        """
        GET /usuarios/perfil/
        Retorna informações do perfil do usuário autenticado
        """
        try:
            # Obter o usuário diretamente do request.user
            usuario = request.user
            
            # Verificar se o usuário foi corretamente autenticado
            if not usuario or usuario.is_anonymous:
                return Response({
                    'erro': 'Usuário não autenticado'
                }, status=status.HTTP_401_UNAUTHORIZED)
            
            serializer = UsuarioSerializer(usuario)
            return Response(serializer.data, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response({
                'erro': 'Erro ao buscar perfil',
                'detalhes': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
    def destroy(self, request, pk=None):
        """
        DELETE /usuarios/{id}/
        Só pode deletar o próprio perfil
        """
        usuario = self.get_object()
        
        # Verificar se o usuário logado é o mesmo que quer deletar
        if usuario.id != request.user.id:
            return Response({
                'erro': 'Você só pode deletar seu próprio perfil'
            }, status=status.HTTP_403_FORBIDDEN)
        
        nome = usuario.nome
        usuario.delete()
        return Response({
            'mensagem': f'Usuário {nome} deletado com sucesso'
        }, status=status.HTTP_200_OK)
    
        
    def partial_update(self, request, pk=None):
        """
        PATCH /usuarios/{id}/
        Só pode atualizar o próprio perfil
        """
        usuario = self.get_object()
        
        # Verificar se é o próprio usuário
        if usuario.id != request.user.id:
            return Response({
                'erro': 'Você só pode atualizar seu próprio perfil'
            }, status=status.HTTP_403_FORBIDDEN)
        
        serializer = CadastroSerializer(
            usuario,
            data=request.data,
            partial=True
        )
        
        if serializer.is_valid():
            serializer.save()
            return Response({
                'mensagem': 'Usuário atualizado com sucesso',
                'usuario': UsuarioSerializer(usuario).data
            }, status=status.HTTP_200_OK)
        
        return Response({
            'erro': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'], 
            url_path='alterar-senha', 
            permission_classes=[IsAuthenticated])
    def alterar_senha(self, request, pk=None):
        """
        POST /usuarios/{id}/alterar-senha/
        Altera a senha do usuário (apenas próprio perfil)
        """
        try:
            usuario = self.get_object()
            
            # Verificar se o usuário logado é o dono do perfil
            if usuario.id != request.user.id:
                return Response({
                    'erro': 'Você só pode alterar sua própria senha'
                }, status=status.HTTP_403_FORBIDDEN)
            
            serializer = AlterarSenhaSerializer(data=request.data)
            
            if serializer.is_valid():
                # Verificar senha atual
                senha_atual = serializer.validated_data.get('senha_atual')
                if not usuario.verificar_senha(senha_atual):
                    return Response({
                        'erro': 'Senha atual incorreta'
                    }, status=status.HTTP_400_BAD_REQUEST)
                
                # Verificar se nova senha é diferente da atual
                nova_senha = serializer.validated_data.get('nova_senha')
                if usuario.verificar_senha(nova_senha):
                    return Response({
                        'erro': 'Nova senha não pode ser igual à senha atual'
                    }, status=status.HTTP_400_BAD_REQUEST)
                
                # Atualizar senha
                usuario.senha = nova_senha
                usuario.save()
                
                return Response({
                    'mensagem': 'Senha alterada com sucesso',
                    'usuario': UsuarioSerializer(usuario).data
                }, status=status.HTTP_200_OK)
            
            return Response({
                'erro': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
            
        except Usuario.DoesNotExist:
            return Response({
                'erro': 'Usuário não encontrado'
            }, status=status.HTTP_404_NOT_FOUND)