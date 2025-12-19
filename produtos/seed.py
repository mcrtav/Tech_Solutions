# produtos/seed.py
import os
import django
import random
from decimal import Decimal

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'setup.settings')
django.setup()

from produtos.models import Produto

def criar_produtos():
    """Cria 10 produtos de teste"""
    
    produtos_teste = [
        {
            'nome': 'Notebook Dell Inspiron',
            'descricao': 'Notebook com processador Intel i5, 8GB RAM, 256GB SSD, tela 15.6" Full HD',
            'marca': 'Dell',
            'preco': Decimal('3499.99')
        },
        {
            'nome': 'Smartphone Samsung Galaxy S23',
            'descricao': 'Smartphone com câmera de 50MP, 256GB armazenamento, 8GB RAM, tela Dynamic AMOLED',
            'marca': 'Samsung',
            'preco': Decimal('4599.00')
        },
        {
            'nome': 'Fone de Ouvido Sony WH-1000XM4',
            'descricao': 'Fone de ouvido com cancelamento de ruído, bateria para 30 horas, Bluetooth 5.0',
            'marca': 'Sony',
            'preco': Decimal('1299.90')
        },
        {
            'nome': 'Smart TV LG 55" 4K',
            'descricao': 'Smart TV 4K UHD, webOS, AI ThinQ, HDR10, Dolby Vision, 3 HDMI, 2 USB',
            'marca': 'LG',
            'preco': Decimal('2899.00')
        },
        {
            'nome': 'Console PlayStation 5',
            'descricao': 'Console de videogame com SSD de 825GB, controle DualSense, saída 8K, Ray Tracing',
            'marca': 'Sony',
            'preco': Decimal('4499.99')
        },
        {
            'nome': 'Câmera Canon EOS R7',
            'descricao': 'Câmera mirrorless 32.5MP, sensor APS-C, gravação 4K, estabilização 8 eixos',
            'marca': 'Canon',
            'preco': Decimal('8999.00')
        },
        {
            'nome': 'Tablet Apple iPad Air',
            'descricao': 'Tablet com chip M1, tela Liquid Retina 10.9", 256GB, Wi-Fi + Cellular',
            'marca': 'Apple',
            'preco': Decimal('6799.00')
        },
        {
            'nome': 'Monitor Gamer Acer Predator',
            'descricao': 'Monitor 27" QHD, 165Hz, 1ms, IPS, NVIDIA G-SYNC Compatible, HDR400',
            'marca': 'Acer',
            'preco': Decimal('2399.99')
        },
        {
            'nome': 'Smartwatch Garmin Forerunner 265',
            'descricao': 'Smartwatch para corrida, GPS, monitor cardíaco, bateria 13 dias, AMOLED touch',
            'marca': 'Garmin',
            'preco': Decimal('2199.00')
        },
        {
            'nome': 'Notebook Gamer Asus ROG Strix',
            'descricao': 'Notebook gamer com RTX 4060, 16GB RAM, 1TB SSD, processador Intel i7, 144Hz',
            'marca': 'Asus',
            'preco': Decimal('9999.00')
        }
    ]
    
    produtos_criados = 0
    
    for produto_data in produtos_teste:
        # Verificar se o produto já existe (para não duplicar)
        if not Produto.objects.filter(
            nome=produto_data['nome'],
            marca=produto_data['marca']
        ).exists():
            
            produto = Produto.objects.create(
                nome=produto_data['nome'],
                descricao=produto_data['descricao'],
                marca=produto_data['marca'],
                preco=produto_data['preco']
            )
            
            produtos_criados += 1
            print(f"✅ Produto criado: {produto.nome} - R${produto.preco}")
        else:
            print(f"⚠️  Produto já existe: {produto_data['nome']}")
    
    return produtos_criados

def limpar_produtos():
    """Remove todos os produtos do banco"""
    total = Produto.objects.count()
    Produto.objects.all().delete()
    print(f"🗑️  {total} produtos removidos do banco")

def listar_produtos():
    """Lista todos os produtos cadastrados"""
    produtos = Produto.objects.all()
    
    print("\n📋 PRODUTOS CADASTRADOS:")
    print("=" * 80)
    
    if not produtos:
        print("Nenhum produto cadastrado.")
        return
    
    for i, produto in enumerate(produtos, 1):
        print(f"{i}. {produto.nome}")
        print(f"   Marca: {produto.marca}")
        print(f"   Preço: R$ {produto.preco:.2f}")
        print(f"   Descrição: {produto.descricao[:80]}..." if len(produto.descricao) > 80 else f"   Descrição: {produto.descricao}")
        print("-" * 80)

if __name__ == "__main__":
    print("=" * 80)
    print("🌱 SEED DE PRODUTOS - Tech Solutions")
    print("=" * 80)
    
    while True:
        print("\nOpções:")
        print("1. Criar 10 produtos de teste")
        print("2. Limpar todos os produtos")
        print("3. Listar produtos cadastrados")
        print("4. Sair")
        
        opcao = input("\nEscolha uma opção (1-4): ").strip()
        
        if opcao == "1":
            print("\n🔄 Criando produtos de teste...")
            criados = criar_produtos()
            print(f"\n🎉 {criados} produtos criados com sucesso!")
        
        elif opcao == "2":
            confirmacao = input("⚠️  Tem certeza que deseja REMOVER TODOS os produtos? (s/n): ").lower()
            if confirmacao == 's':
                limpar_produtos()
            else:
                print("Operação cancelada.")
        
        elif opcao == "3":
            listar_produtos()
        
        elif opcao == "4":
            print("\n👋 Até logo!")
            break
        
        else:
            print("❌ Opção inválida. Tente novamente.")