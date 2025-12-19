from rest_framework import viewsets, status
# esse import é como vamos usar a rota
from rest_framework.response import Response
# esse import é como vamos dar a resposta
from rest_framework.decorators import action
# esse import é para criar rotas extras
from rest_framework.permissions import AllowAny, IsAuthenticated #IsAdminUser
# esse import mexe com permissões 
# (quem pode usar as rotas)
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError

from usuarios.models import Usuario
from usuarios.serializers import (
	UsuarioSerializer,
	LoginSerializer,
	CadastroSerializer,
	LoginResponseSerializer)

#from produtos.serializers import (CrarProduto)
# ATENÇÃO TUDO QUE É USUARIO VIRA PRODUTO

class UsuarioViewSets(viewsets.ModelViewSet):
	# apresente o modelo do banco, junto com 
	# todas as entradas (todos os objetos)
	queryset = Usuario.objects.all()
	# regras do jogo: quais restrições que cada
	# rota irá ter
	serializer_class = UsuarioSerializer

	def get_permissions(self):
		'''
		Define permissões por action
		--cadastro e login: publica (AllowAny)
		--list (listar) e retrive (buscar): publica (AllowAny)
		-- update, partial_update, destroy (delete): privado (IsAuthenticated)
		'''
		if self.action in ['cadastro', 'login',
			'list', 'retrieve', 'refresh_token']:
			permission_classes = [AllowAny]
		else:
			permission_classes = [IsAuthenticated]

		return [permission() for permission in
				permission_classes]

	# criar rotas extras -> ideia de usuarios/rota

	# action de cadastro (não é necessario,
	# mas fica mais organizado)
	
	@action(detail=False, methods=['post'],
			url_path='cadastro', 
			serializer_class=CadastroSerializer)
	def cadastro(self, request):
		# passando os dados do cadastro para
		# o serializer validar
		serializer = CadastroSerializer(
			data=request.data
		)

		if serializer.is_valid():
			# cadastrar -> criar o usuario no banco
			usuario = serializer.save()
			return Response(
				{
					'mensagem':'Usuario cadastrado com sucesso',
					'usuario': UsuarioSerializer(usuario).data
				}, status=status.HTTP_201_CREATED)
		
		return Response({
			'erro':serializer.errors
		}, status=status.HTTP_400_BAD_REQUEST)
	

	# action de Login
	@action(detail=False, methods=['post'],
			url_path='login',
			serializer_class=LoginSerializer)
	def login(self, request):
		# 1º passo -> pegar os dados e verificar
		serializer = LoginSerializer(
			data=request.data
		)
		# 2º passo -> ver se esta tudo valido
		if serializer.is_valid():
			usuario = \
			serializer.validated_data['usuario']

			# 3º passo -> criar o token
			refresh = RefreshToken.for_user(usuario)
			access = refresh.access_token

			return Response({
				'mensagem':'Login realizado com sucesso',
				'usuario':UsuarioSerializer(usuario).data,
				'access': str(access),
				'refresh': str(refresh)
			}, status=status.HTTP_200_OK)

		return Response({
			'erro':serializer.errors
		}, status=status.HTTP_401_UNAUTHORIZED)

	@action(detail=False, methods=['post'],
			url_path='refresh', 
			permission_classes=[AllowAny])
	def refresh_token(self, request):
		
		'''
		Gera um novo token de acesso usando o 
		refresh token

		Recebe o refresh
		Envia o access (resposta 200)
		'''

		# 1º passo -> receber o refresh
		refresh_token = request.data.get('refresh')

		# 2º passo -> verificar
		if not refresh_token:
			return Response({
				'erro':'Refresh Token é obrigatório'
			}, status=status.HTTP_400_BAD_REQUEST)
		
		try:
			refresh = RefreshToken(refresh_token)
			user_id = refresh['user_id']

			usuario = Usuario.objects.get(id=user_id)
			
			# Gerar novo token de acesso forçando o JWT
			# pelo fato de impedir que ele volte a buscar
			# no auth_user

			from rest_framework_simplejwt.tokens import \
			AccessToken

			new_token_access = AccessToken.for_user(usuario)

			return Response({
				'access':str(new_token_access)
			}, status=status.HTTP_200_OK)
		except TokenError:
			return Response({
				'erro': 'Token inválido ou expirado'
			}, status=status.HTTP_401_UNAUTHORIZED)
		
	# mudanças em relação a autenticação no
	# delete (destroy) e update (partial_update)

	def destroy(self, request, pk=None):
		'''
		DELETE 
		Só pode deletar o próprio perfil/user
		'''
		usuario = self.get_object()

		# verificar se o usuario logado
		# é o mesmo que quer deletar
		user_id = request.auth.payload.get('user_id')
		if usuario.id != user_id:
			return Response({
				'erro': 'Você só pode deletar seu próprio perfil'
			}, status=status.HTTP_403_FORBIDDEN)
		
		nome = usuario.nome
		usuario.delete()
		return Response({
			'mensagem': f'Usuário {nome} deletado com sucesso'
		}, status=status.HTTP_200_OK)

	def partial_update(self, request, pk=None):
		'''
		PATCH
		Só pode atualizar o próprio perfil/user
		'''

		usuario = self.get_object()

		# verificar se é o próprio usuário
		user_id = request.auth.payload.get('user_id')
		if usuario.id != user_id:
			return Response({
				'erro':'Você só pode atualizar '\
				'seu próprio perfil'
			}, status=status.HTTP_403_FORBIDDEN)
		# caminho feliz
		serializer = CadastroSerializer(
			usuario, # usuario em questão
			data=request.data, # passo as mudanças
			partial=True # permito que mude só alguns campos
		)

		if serializer.is_valid():
			serializer.save()
			return Response({
				'mensagem':'Usuário atualizado com sucesso',
				'usuario': UsuarioSerializer(usuario).data
			}, status=status.HTTP_200_OK)
		# caminho triste onde o usuario quer mudar
		# algo dele, mas não consegue
		return Response({
			'erro': serializer.errors
		}, status=status.HTTP_400_BAD_REQUEST)

	@action(detail=False, methods=['get'],
			url_path='perfil',
			permission_classes=[IsAuthenticated])
	def perfil(self, request):
		'''
		Retorna as informações do perfil do usuário autenticado
		'''
		# Pegar o id do usuario dentro do token
		user_id = request.auth.payload.get('user_id')

		try:
			# ir no banco, achar o user_id lá

			usuario = Usuario.objects.get(id=user_id)
			serializer = UsuarioSerializer(usuario)

			return Response(serializer.data,
							status=status.HTTP_200_OK)
		except Usuario.DoesNotExist:
			return Response({
				'erro':'Usuário não encontrado'
			}, status=status.HTTP_404_NOT_FOUND)