# usuarios/serializers.py
from rest_framework import serializers
from usuarios.models import Usuario
import re

class CadastroSerializer(serializers.ModelSerializer):
    # "equivale" ao to_dict do Flask 
    # (só que mais poderoso)

    senha = serializers.CharField(
        min_length=8,
        max_length=50,
        write_only=True,  # Não aparece na saida
        style={'input_type': 'password'}
    )
    
    senha_confirmacao = serializers.CharField(
        write_only=True,
        style={'input_type': 'password'}
    )
    
    telefone = serializers.CharField(
        required=False,  # Não é obrigatório
        allow_blank=True,
        allow_null=True,
        max_length=15,
        help_text='Formato: (XX) XXXXX-XXXX'
    )

    class Meta:
        model = Usuario  # Qual modelo vai serializar
        fields = ['id', 'nome', 'email', 'telefone', 'senha',
                  'criado', 'atualizado', 'senha_confirmacao']
        
        # Informar os campos de apenas leitura
        # Não podem ser modificados
        read_only_fields = ['id', 'criado', 'atualizado']
    
    def validate_nome(self, value):
        # validar o campo nome
        value = value.strip()
        if len(value) < 3:
            raise serializers.ValidationError(
                'Nome deve ter no mínimo 3 caracteres'
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
        
        # Validação adicional: pelo menos uma letra maiúscula
        if not any(c.isupper() for c in value):
            raise serializers.ValidationError(
                'Senha deve conter pelo menos uma letra maiúscula'
            )
        
        return value
    
    def validate_telefone(self, value):
        """
        Valida o formato do telefone usando regex
        Formato esperado: (XX) XXXXX-XXXX
        """
        if value:  # Se o telefone foi fornecido
            value = value.strip()
            
            # Regex para formato (XX) XXXXX-XXXX
            padrao = r'^\(\d{2}\) \d{5}-\d{4}$'
            
            if not re.match(padrao, value):
                raise serializers.ValidationError(
                    'Telefone deve estar no formato (XX) XXXXX-XXXX. Exemplo: (11) 98765-4321'
                )
            
            # Verificar se o DDD é válido (11-99)
            ddd = value[1:3]
            if not (11 <= int(ddd) <= 99):
                raise serializers.ValidationError(
                    'DDD inválido. Deve estar entre 11 e 99'
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
        
        # Formatar telefone se fornecido
        if 'telefone' in validated_data and validated_data['telefone']:
            telefone = validated_data['telefone']
            # Garantir que está no formato correto
            if not re.match(r'^\(\d{2}\) \d{5}-\d{4}$', telefone):
                # Tentar formatar automaticamente
                numeros = ''.join(filter(str.isdigit, telefone))
                if len(numeros) == 11:
                    validated_data['telefone'] = f'({numeros[:2]}) {numeros[2:7]}-{numeros[7:]}'
        
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
        style={'input_type': 'password'}
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
    telefone_formatado = serializers.SerializerMethodField()
    
    class Meta:
        model = Usuario
        fields = ['id', 'nome', 'email', 'telefone', 'telefone_formatado', 'criado']
        read_only_fields = ['id', 'criado']
    
    def get_telefone_formatado(self, obj):
        """
        Retorna o telefone formatado
        """
        return obj.formatar_telefone() if obj.telefone else None


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


    # usuarios/serializers.py - ADICIONE ESTES SERIALIZERS
class EsqueciSenhaSerializer(serializers.Serializer):
    """
    Serializer para solicitar recuperação de senha
    """
    email = serializers.EmailField(
        required=True,
        help_text='E-mail do usuário para recuperação de senha'
    )
    
    def validate_email(self, value):
        """
        Verifica se o e-mail existe no sistema
        """
        email = value.lower().strip()
        
        if not Usuario.objects.filter(email=email).exists():
            # Por segurança, não revelamos se o e-mail existe ou não
            raise serializers.ValidationError(
                'Se o e-mail estiver cadastrado, você receberá um link de recuperação'
            )
        
        return email


class ValidarTokenSerializer(serializers.Serializer):
    """
    Serializer para validar token de recuperação
    """
    token = serializers.CharField(
        required=True,
        max_length=100,
        help_text='Token de recuperação recebido por e-mail'
    )
    
    email = serializers.EmailField(
        required=True,
        help_text='E-mail do usuário'
    )
    
    def validate(self, data):
        email = data['email'].lower().strip()
        token = data['token'].strip()
        
        try:
            usuario = Usuario.objects.get(email=email)
        except Usuario.DoesNotExist:
            raise serializers.ValidationError({
                'email': 'Usuário não encontrado'
            })
        
        if not usuario.validar_token_recuperacao(token):
            raise serializers.ValidationError({
                'token': 'Token inválido ou expirado'
            })
        
        data['usuario'] = usuario
        return data


class RedefinirSenhaSerializer(serializers.Serializer):
    """
    Serializer para redefinir a senha usando token
    """
    email = serializers.EmailField(
        required=True,
        help_text='E-mail do usuário'
    )
    
    token = serializers.CharField(
        required=True,
        max_length=100,
        help_text='Token de recuperação recebido por e-mail'
    )
    
    nova_senha = serializers.CharField(
        required=True,
        write_only=True,
        style={'input_type': 'password'},
        help_text='Nova senha forte (mínimo 8 caracteres: 1 maiúscula, 1 minúscula, 1 número, 1 especial)'
    )
    
    confirmar_senha = serializers.CharField(
        required=True,
        write_only=True,
        style={'input_type': 'password'},
        help_text='Confirmação da nova senha'
    )
    
    def validate_nova_senha(self, value):
        """Valida senha forte"""
        # Reutiliza a validação do CadastroSerializer
        if len(value) < 8:
            raise serializers.ValidationError('Senha deve ter no mínimo 8 caracteres')
        
        if not re.search(r'[A-Z]', value):
            raise serializers.ValidationError('Senha deve conter pelo menos uma letra maiúscula (A-Z)')
        
        if not re.search(r'[a-z]', value):
            raise serializers.ValidationError('Senha deve conter pelo menos uma letra minúscula (a-z)')
        
        if not re.search(r'\d', value):
            raise serializers.ValidationError('Senha deve conter pelo menos um número (0-9)')
        
        if not re.search(r'[@$!%*?&]', value):
            raise serializers.ValidationError('Senha deve conter pelo menos um caractere especial (@ $ ! % * ? &)')
        
        if not re.match(r'^[A-Za-z0-9@$!%*?&]+$', value):
            raise serializers.ValidationError('Senha contém caracteres não permitidos')
        
        return value
    
    def validate(self, data):
        email = data['email'].lower().strip()
        token = data['token'].strip()
        nova_senha = data['nova_senha']
        confirmar_senha = data['confirmar_senha']
        
        # Verificar se as senhas coincidem
        if nova_senha != confirmar_senha:
            raise serializers.ValidationError({
                'confirmar_senha': 'As senhas não coincidem'
            })
        
        # Verificar token e usuário
        try:
            usuario = Usuario.objects.get(email=email)
        except Usuario.DoesNotExist:
            raise serializers.ValidationError({
                'email': 'Usuário não encontrado'
            })
        
        if not usuario.validar_token_recuperacao(token):
            raise serializers.ValidationError({
                'token': 'Token inválido ou expirado'
            })
        
        # Verificar se a nova senha é diferente da atual
        if usuario.verificar_senha(nova_senha):
            raise serializers.ValidationError({
                'nova_senha': 'Nova senha não pode ser igual à senha atual'
            })
        
        data['usuario'] = usuario
        return data
    

    # usuarios/serializers.py - ADICIONE ESTE SERIALIZER ANTES DO FIM DO ARQUIVO
class AlterarSenhaSerializer(serializers.Serializer):
    """Serializer específico para alteração de senha dentro do perfil"""
    senha_atual = serializers.CharField(
        required=True,
        write_only=True,
        style={'input_type': 'password'},
        help_text='Senha atual do usuário'
    )
    
    nova_senha = serializers.CharField(
        required=True,
        write_only=True,
        style={'input_type': 'password'},
        help_text='Nova senha forte (mínimo 8 caracteres: 1 maiúscula, 1 minúscula, 1 número, 1 especial)'
    )
    
    confirmar_senha = serializers.CharField(
        required=True,
        write_only=True,
        style={'input_type': 'password'},
        help_text='Confirmação da nova senha'
    )
    
    def validate_nova_senha(self, value):
        """Valida senha forte"""
        # Copiar a lógica de validação de senha do CadastroSerializer
        # para evitar importação circular
        
        # Verificar comprimento mínimo
        if len(value) < 8:
            raise serializers.ValidationError('Senha deve ter no mínimo 8 caracteres')
        
        # Verificar se tem pelo menos uma letra maiúscula
        if not re.search(r'[A-Z]', value):
            raise serializers.ValidationError('Senha deve conter pelo menos uma letra maiúscula (A-Z)')
        
        # Verificar se tem pelo menos uma letra minúscula
        if not re.search(r'[a-z]', value):
            raise serializers.ValidationError('Senha deve conter pelo menos uma letra minúscula (a-z)')
        
        # Verificar se tem pelo menos um número
        if not re.search(r'\d', value):
            raise serializers.ValidationError('Senha deve conter pelo menos um número (0-9)')
        
        # Verificar se tem pelo menos um caractere especial
        if not re.search(r'[@$!%*?&]', value):
            raise serializers.ValidationError('Senha deve conter pelo menos um caractere especial (@ $ ! % * ? &)')
        
        # Verificar se contém apenas caracteres permitidos
        if not re.match(r'^[A-Za-z0-9@$!%*?&]+$', value):
            raise serializers.ValidationError('Senha contém caracteres não permitidos')
        
        return value
    
    def validate(self, data):
        nova_senha = data.get('nova_senha')
        confirmar_senha = data.get('confirmar_senha')
        
        if nova_senha != confirmar_senha:
            raise serializers.ValidationError({
                'confirmar_senha': 'As novas senhas não coincidem'
            })
        
        return data