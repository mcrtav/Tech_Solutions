# produtos/management/commands/seed_produtos.py
from django.core.management.base import BaseCommand
from django.db import transaction
from decimal import Decimal
import random

from produtos.models import Produto

class Command(BaseCommand):
    help = 'Popula o banco de dados com produtos de teste'

    def add_arguments(self, parser):
        parser.add_argument(
            '--quantidade',
            type=int,
            default=10,
            help='Número de produtos a criar (padrão: 10)'
        )
        parser.add_argument(
            '--limpar',
            action='store_true',
            help='Limpar todos os produtos antes de criar novos'
        )

    def handle(self, *args, **options):
        quantidade = options['quantidade']
        limpar = options['limpar']

        # Produtos pré-definidos para garantir qualidade
        produtos_base = [
            {
                'nome': 'Notebook Dell Inspiron',
                'descricao': 'Notebook com processador Intel i5, 8GB RAM, 256GB SSD, tela 15.6" Full HD. Ideal para trabalho e estudos.',
                'marca': 'Dell',
                'preco_min': 3000,
                'preco_max': 4000
            },
            {
                'nome': 'Smartphone Samsung Galaxy',
                'descricao': 'Smartphone com câmera de alta resolução, armazenamento generoso e tela AMOLED de qualidade.',
                'marca': 'Samsung',
                'preco_min': 2000,
                'preco_max': 5000
            },
            {
                'nome': 'Fone de Ouvido Bluetooth',
                'descricao': 'Fone de ouvido sem fio com cancelamento de ruído ativo e bateria de longa duração.',
                'marca': 'Sony',
                'preco_min': 800,
                'preco_max': 1500
            },
            {
                'nome': 'Smart TV LED',
                'descricao': 'Smart TV com resolução 4K, sistema operacional inteligente e múltiplas entradas HDMI.',
                'marca': 'LG',
                'preco_min': 2500,
                'preco_max': 4000
            },
            {
                'nome': 'Console de Videogame',
                'descricao': 'Console de última geração com gráficos avançados, SSD rápido e compatibilidade com jogos em 4K.',
                'marca': 'Sony',
                'preco_min': 4000,
                'preco_max': 5000
            },
            {
                'nome': 'Câmera Digital DSLR',
                'descricao': 'Câmera profissional com sensor full-frame, gravação em 4K e múltiplas lentes intercambiáveis.',
                'marca': 'Canon',
                'preco_min': 6000,
                'preco_max': 10000
            },
            {
                'nome': 'Tablet Android',
                'descricao': 'Tablet com tela de alta resolução, processador rápido e bateria que dura o dia todo.',
                'marca': 'Samsung',
                'preco_min': 1500,
                'preco_max': 3000
            },
            {
                'nome': 'Monitor Gamer',
                'descricao': 'Monitor com alta taxa de atualização, tempo de resposta rápido e tecnologia de sincronização adaptativa.',
                'marca': 'Acer',
                'preco_min': 1800,
                'preco_max': 3000
            },
            {
                'nome': 'Smartwatch Esportivo',
                'descricao': 'Smartwatch com GPS integrado, monitor cardíaco, resistência à água e múltiplos modos esportivos.',
                'marca': 'Garmin',
                'preco_min': 1500,
                'preco_max': 2500
            },
            {
                'nome': 'Notebook Gamer',
                'descricao': 'Notebook com placa de vídeo dedicada, processador de alta performance e sistema de refrigeração avançado.',
                'marca': 'Asus',
                'preco_min': 7000,
                'preco_max': 12000
            }
        ]

        # Adicionar variações
        modelos = ['Pro', 'Max', 'Lite', 'Ultra', 'Plus', 'Elite']
        cores = ['Preto', 'Branco', 'Prata', 'Azul', 'Vermelho', 'Verde']

        with transaction.atomic():
            if limpar:
                self.stdout.write('Limpando produtos existentes...')
                Produto.objects.all().delete()
                self.stdout.write(self.style.SUCCESS('Produtos removidos com sucesso!'))

            produtos_criados = 0

            for i in range(quantidade):
                base = random.choice(produtos_base)
                modelo = random.choice(modelos)
                cor = random.choice(cores)
                
                # Criar nome único
                nome = f"{base['nome']} {modelo} {cor}"
                
                # Gerar preço aleatório
                preco = Decimal(str(random.uniform(base['preco_min'], base['preco_max']))).quantize(Decimal('0.01'))
                
                # Verificar se já existe
                if not Produto.objects.filter(nome=nome).exists():
                    Produto.objects.create(
                        nome=nome,
                        descricao=base['descricao'] + f" Modelo {modelo} na cor {cor}.",
                        marca=base['marca'],
                        preco=preco
                    )
                    produtos_criados += 1
                    self.stdout.write(f'✅ Criado: {nome} - R${preco:.2f}')

            self.stdout.write(
                self.style.SUCCESS(
                    f'\n🎉 Seed concluído! {produtos_criados} produtos criados com sucesso!'
                )
            )