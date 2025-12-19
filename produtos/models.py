from django.db import models

class Produto(models.Model):
    
    nome = models.CharField(max_length=60,
                    verbose_name='Nome',
                    help_text='Nome completo do produto',
                    null=False)
    descricao = models.TextField(
                    verbose_name='Descrição',
                    help_text='Descrição completa do produto',
                    null=False)
    marca = models.CharField(max_length=60,
                    verbose_name='Marca',
                    help_text='Marca do Produto',
                    null=False)
    preco = models.DecimalField(max_digits=6, decimal_places=2,
                    verbose_name='Preço',
                    help_text='Preço do Produto',
                    null=False)
    criado = models.DateTimeField(auto_now_add=True,
                    verbose_name='Criado em')
    atualizado = models.DateTimeField(auto_now=True,
                    verbose_name='Atualizado em')
    
    class Meta:
        # nome da tabela
        db_table = 'produtos'
        verbose_name = 'Produto'
        verbose_name_plural = 'Produtos'
        ordering = ['nome'] #ordena por nome (ordem alfabetica)
       
    
    def __repr__(self):
        """
        Retorna uma string representativa do objeto, no formato
        "<nome>".
        """
        return f'<Produto {self.nome}>'
    
    