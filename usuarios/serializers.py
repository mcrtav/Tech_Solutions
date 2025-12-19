from rest_framework import serializers
from usuarios.models import Usuario
# from produtos.models  import Produtos

class CadastroSerializer(
    serializers.ModelSerializer):
    # "equivale" ao to_dict do Flask 
    # (só que mais poderoso)

    senha = serializers.CharField(
        min_length=8,
        max_length=50,
        write_only=True, # Não aparece na saida
        style = {'input_type': 'password'}
    )
    senha_confirmacao = serializers.CharField(
        write_only=True,
        style = {'input_type': 'password'}
    )

    class Meta:
        model = Usuario # Qual modelo vai serializar
        fields = ['id', 'nome', 'email', 'senha',
            'criado', 'atualizado', 'senha_confirmacao']
        
        # todas as colunas do banco
        # fields = '__all__'

        # se quisesse pegar varias colunas
        # exceto algumas
        # exclude = ['senha']

        # Informar os campos de apenas leitura
        # Não podem ser modificados
        read_only_fields = ['id', 'criado',
                      'atualizado']
    
    def validate_nome(self, value):
        # validar o campo nome
        value = value.strip()
        if len(value) < 3:
            raise serializers.ValidationError(
                'Nome deve ter no mínimo 3 ' \
                'caracteres'
            )
        return value
    
    def validate_email(self, value):
        email_criacao = value.lower().strip()
        # verificar se o email existe
        if Usuario.objects.filter(
            email=email_criacao).exists():
            raise serializers.ValidationError(
                'Este email já está cadastrado'
            )
        return email_criacao
    
    def validate_senha(self, value):
        if value.isdigit():
            raise serializers.ValidationError(
                'Senha não pode ser apenas números'
            )
        if len(value) < 8:
            raise serializers.ValidationError(
                'Senha deve ter no mínimo 8 caracteres'
            )
        return value
    
    def validate(self, data):

        senha = data.get('senha')
        senha_confirmacao = data.get('senha_confirmacao')

        if senha != senha_confirmacao:
            raise serializers.ValidationError({
                'senha_confirmacao':
                'As senhas não coincidem'
            })
        # remover o que não faz parte do modelo
        data.pop('senha_confirmacao')
        return data

    def create(self, validated_data):
        validated_data.pop('senha_confirmacao', None)
        return Usuario.objects.create(**validated_data)

    def update(self, instance, validated_data):
        '''
        Ao atualizar, verifica se a senha é diferente 
        '''
        if 'senha' in validated_data:
            if instance.verificar_senha(
                validated_data['senha']):
                # chamar o metodo verificar_senha do modelo
                # e passar a senha digitada
                raise serializers.ValidationError({
                    'senha': 'Nova senha não pode ser igual a anterior'
                })
        # atualizar senha do usuario
        for campo, valor in validated_data.items():
            setattr(instance, campo, valor)
        instance.save()
        return instance
    
class LoginSerializer(serializers.Serializer):
    '''
    Essa classe não faz parte do Model
    Apenas valida login
    '''
    email = serializers.EmailField(
        required=True
    )
    senha = serializers.CharField(
        required=True,
        write_only=True,
        style={'input_type':'password'}
    )

    def validate(self, data):
        email_login = data.get('email').lower().strip()
        senha_login = data.get('senha')

        # 1º passo -> buscar o usuário
        try:
            usuario = Usuario.objects.get(
                email=email_login)
        except Usuario.DoesNotExist:
            raise serializers.ValidationError(
                'Email ou senha inválidos'
            )
        
        # 2º passo -> verificar a senha
        if not usuario.verificar_senha(senha_login):
            # caso a senha digitada não seja a correta
            raise serializers.ValidationError(
                'Email ou senha inválidos'
            )
        # 3º passo: adicionar o usuario aos dados validados
        data['usuario'] = usuario
        return data
    
class UsuarioSerializer(serializers.ModelSerializer):
    '''
    Serializer para retornar dados do usuário
    '''
    class Meta:
        model = Usuario
        fields = ['id', 'nome', 'email', 'criado']
        read_only_fields = ['id', 'criado']

class LoginResponseSerializer(serializers.Serializer):
    '''
    Resposta do Login (apenas para documentação 
    da API)
    '''
    mensagem = serializers.CharField()
    usuario = UsuarioSerializer()
    access = serializers.CharField(
        help_text='Token de acesso JWT'
    )
    refresh = serializers.CharField(
        help_text='Token de refresh JWT'
    )

# class CriarProdutos olhar  ->  CadastroSerializer

# class