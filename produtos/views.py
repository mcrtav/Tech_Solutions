from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from django.db.models import Q

from produtos.models import Produto
from produtos.serializers import ProdutoSerializer

class ProdutoViewSets(viewsets.ModelViewSet):  # ✅ HERDAR CORRETAMENTE
    """
    ViewSet completo para gerenciamento de produtos
    """
    queryset = Produto.objects.all()  # ✅ DEFINIR QUERYSET
    serializer_class = ProdutoSerializer  # ✅ DEFINIR SERIALIZER
    permission_classes = [IsAuthenticatedOrReadOnly]  # ✅ PERMISSÕES
    
    # ============ ROTAS PERSONALIZADAS ============
    
    @action(detail=False, methods=['get'], url_path='buscar')
    def buscar(self, request):
        """
        GET /produtos/buscar/ - Busca produtos por nome ou marca
        """
        nome = request.query_params.get('nome', '').strip()
        marca = request.query_params.get('marca', '').strip()
        
        queryset = Produto.objects.all()
        
        if nome:
            queryset = queryset.filter(nome__icontains=nome)
        if marca:
            queryset = queryset.filter(marca__icontains=marca)
        
        total = queryset.count()
        
        if total == 0:
            return Response({
                'mensagem': 'Nenhum produto encontrado',
                'total': 0,
                'produtos': []
            }, status=status.HTTP_200_OK)
        
        serializer = self.get_serializer(queryset, many=True)
        
        return Response({
            'mensagem': f'Encontrados {total} produto(s)',
            'total': total,
            'produtos': serializer.data
        }, status=status.HTTP_200_OK)
    
    @action(detail=False, methods=['get'], url_path='estatisticas')
    def estatisticas(self, request):
        """
        GET /produtos/estatisticas/ - Estatísticas dos produtos
        """
        from django.db.models import Avg, Max, Min, Count
        
        total = Produto.objects.count()
        
        if total == 0:
            return Response({
                'mensagem': 'Nenhum produto cadastrado',
                'total_produtos': 0
            }, status=status.HTTP_200_OK)
        
        estatisticas = Produto.objects.aggregate(
            preco_medio=Avg('preco'),
            preco_maximo=Max('preco'),
            preco_minimo=Min('preco')
        )
        
        return Response({
            'mensagem': f'Estatísticas de {total} produto(s)',
            'total_produtos': total,
            'preco_medio': float(estatisticas['preco_medio']) if estatisticas['preco_medio'] else 0,
            'preco_maximo': float(estatisticas['preco_maximo']) if estatisticas['preco_maximo'] else 0,
            'preco_minimo': float(estatisticas['preco_minimo']) if estatisticas['preco_minimo'] else 0
        }, status=status.HTTP_200_OK)
    
    # ============ SOBRESCREVER MÉTODOS PARA MELHOR CONTROLE ============
    
    def list(self, request):
        """
        GET /produtos/ - Lista todos os produtos
        """
        search_param = request.query_params.get('search', None)
        queryset = self.get_queryset()
        
        if search_param:
            queryset = queryset.filter(
                Q(nome__icontains=search_param) | 
                Q(marca__icontains=search_param)
            )
            mensagem = f'Busca por "{search_param}" - {queryset.count()} resultado(s)'
        else:
            mensagem = f'Total de produtos: {queryset.count()}'
        
        serializer = self.get_serializer(queryset, many=True)
        return Response({
            'mensagem': mensagem,
            'total': queryset.count(),
            'produtos': serializer.data
        }, status=status.HTTP_200_OK)
    
    def retrieve(self, request, pk=None):
        """
        GET /produtos/{id}/ - Busca produto por ID
        """
        try:
            produto = self.get_object()
            serializer = self.get_serializer(produto)
            return Response({
                'mensagem': 'Produto encontrado',
                'produto': serializer.data
            }, status=status.HTTP_200_OK)
        except Produto.DoesNotExist:
            return Response({
                'erro': 'Produto não encontrado'
            }, status=status.HTTP_404_NOT_FOUND)
    
    def create(self, request):
        """
        POST /produtos/ - Cria novo produto
        """
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            produto = serializer.save()
            return Response({
                'mensagem': 'Produto criado com sucesso',
                'produto': serializer.data
            }, status=status.HTTP_201_CREATED)
        
        return Response({
            'erro': 'Falha ao criar produto',
            'detalhes': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)
    
    def update(self, request, pk=None):
        """
        PUT /produtos/{id}/ - Atualiza produto completamente
        """
        try:
            produto = self.get_object()
        except Produto.DoesNotExist:
            return Response({
                'erro': 'Produto não encontrado'
            }, status=status.HTTP_404_NOT_FOUND)
        
        serializer = self.get_serializer(produto, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({
                'mensagem': 'Produto atualizado com sucesso',
                'produto': serializer.data
            }, status=status.HTTP_200_OK)
        
        return Response({
            'erro': 'Falha ao atualizar produto',
            'detalhes': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)
    
    def partial_update(self, request, pk=None):
        """
        PATCH /produtos/{id}/ - Atualiza produto parcialmente
        """
        try:
            produto = self.get_object()
        except Produto.DoesNotExist:
            return Response({
                'erro': 'Produto não encontrado'
            }, status=status.HTTP_404_NOT_FOUND)
        
        serializer = self.get_serializer(produto, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({
                'mensagem': 'Produto atualizado parcialmente',
                'produto': serializer.data
            }, status=status.HTTP_200_OK)
        
        return Response({
            'erro': 'Falha ao atualizar produto',
            'detalhes': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)
    
    def destroy(self, request, pk=None):
        """
        DELETE /produtos/{id}/ - Remove um produto
        """
        try:
            produto = self.get_object()
            produto_nome = produto.nome
            produto.delete()
            return Response({
                'mensagem': f'Produto "{produto_nome}" removido com sucesso'
            }, status=status.HTTP_200_OK)
        except Produto.DoesNotExist:
            return Response({
                'erro': 'Produto não encontrado'
            }, status=status.HTTP_404_NOT_FOUND)