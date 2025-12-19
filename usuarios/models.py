# usuarios/models.py
from django.db import models
from django.core.validators import RegexValidator
from django.contrib.auth.hashers import make_password, check_password

class Usuario(models.Model):
    
    nome = models.CharField(max_length=80,
                    verbose_name='Nome',
                    help_text='Nome completo do usuário',
                    null=False)
    
    email = models.EmailField(unique=True, 
                    verbose_name='E-mail',
                    help_text='E-mail do usuário',
                    null=False)
    
    telefone = models.CharField(
        max_length=15,
        verbose_name='Telefone',
        help_text='Telefone no formato (XX) XXXXX-XXXX',
        null=True,  # Pode ser nulo inicialmente
        blank=True,
        validators=[
            RegexValidator(
                regex=r'^\(\d{2}\) \d{5}-\d{4}$',
                message='Telefone deve estar no formato (XX) XXXXX-XXXX'
            )
        ]
    )
    
    senha = models.CharField(max_length=255,
                    verbose_name='Senha',
                    help_text='Senha do usuário',
                    null=False)
    
    criado = models.DateTimeField(auto_now_add=True,
                    verbose_name='Criado em')
    
    atualizado = models.DateTimeField(auto_now=True,
                    verbose_name='Atualizado em')
    
    class Meta:
        # nome da tabela
        db_table = 'usuarios'
        verbose_name = 'Usuário'
        verbose_name_plural = 'Usuários'
        ordering = ['nome']  # ordena por nome (ordem alfabetica)
    
    def __repr__(self):
        """
        Retorna uma string representativa do objeto, no formato
        "<nome>".
        """
        return f'<Usuario {self.nome}>'
    
    def __str__(self):
        """
        Retorna uma string representativa do objeto, no formato
        "<nome> (<email>)".
        """
        return f'{self.nome} ({self.email})'

    def verificar_senha(self, senha_texto):
        return check_password(senha_texto, self.senha)
        
    def save(self, *args, **kwargs):
        # args = argumentos posicionais
        # kwargs = argumentos nomeados
        if self.senha and not \
        self.senha.startswith('pbkdf2_sha256'):
            # se a senha for alterada
            self.senha = make_password(self.senha)
        # se a senha for criada ou atualizada
        # chama o save da superclasse
        super().save(*args, **kwargs)

    # criar a verificação se o usuário está autenticado
    # Isso faz com que qualquer instancia (objeto) desse 
    # modelo seja considerada autenticada pelo Django

    @property
    def is_authenticated(self):
        '''
        Retorna True sempre, pois objetos (usuario) só existem
        se autenticados
        '''
        return True
    
    @property
    def is_anonymous(self):
        '''
        Retorna False sempre, pois não aceita objeto (usuario)
        anonimo 
        Isso informa ao Django que esse objeto não é do tipo
        especial "AnonymousUser" (que representa usuários não
        logados)
        '''
        return False
    
    def formatar_telefone(self):
        """
        Retorna o telefone formatado
        """
        if self.telefone:
            # Remove caracteres não numéricos e formata
            numeros = ''.join(filter(str.isdigit, self.telefone))
            if len(numeros) == 11:
                return f'({numeros[:2]}) {numeros[2:7]}-{numeros[7:]}'
        return self.telefone