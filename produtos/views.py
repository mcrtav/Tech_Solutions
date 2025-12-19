# produtos/views.py
from rest_framework import viewsets, status, filters
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticatedOrReadOnly

from produtos.models import Produto
from produtos.serializers import ProdutoSerializer

class ProdutoViewSets(viewsets.ModelViewSet):
    queryset = Produto.objects.all()
    serializer_class = ProdutoSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends = [filters.SearchFilter]
    search_fields = ['nome', 'marca']
    
    def create(self, request):
        """
        Cria um novo produto
        """
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({
                'mensagem': 'Produto criado com sucesso',
                'produto': serializer.data
            }, status=status.HTTP_201_CREATED)
        return Response({
            'erro': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)
    
    def list(self, request):
        """
        Lista todos os produtos com suporte a busca
        """
        queryset = self.filter_queryset(self.get_queryset())
        
        # Busca por nome ou marca
        search_param = request.query_params.get('search', None)
        if search_param:
            queryset = queryset.filter(
                models.Q(nome__icontains=search_param) | 
                models.Q(marca__icontains=search_param)
            )
        
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
    def retrieve(self, request, pk=None):
        """
        Busca um produto específico por ID
        """
        try:
            produto = Produto.objects.get(id=pk)
            serializer = self.get_serializer(produto)
            return Response(serializer.data)
        except Produto.DoesNotExist:
            return Response({
                'erro': 'Produto não encontrado'
            }, status=status.HTTP_404_NOT_FOUND)
    
    def update(self, request, pk=None):
        """
        Atualiza um produto completo
        """
        try:
            produto = Produto.objects.get(id=pk)
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
            })
        return Response({
            'erro': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)
    
    def partial_update(self, request, pk=None):
        """
        Atualiza parcialmente um produto
        """
        try:
            produto = Produto.objects.get(id=pk)
        except Produto.DoesNotExist:
            return Response({
                'erro': 'Produto não encontrado'
            }, status=status.HTTP_404_NOT_FOUND)
        
        serializer = self.get_serializer(produto, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({
                'mensagem': 'Produto atualizado parcialmente com sucesso',
                'produto': serializer.data
            })
        return Response({
            'erro': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)
    
    def destroy(self, request, pk=None):
        """
        Remove um produto
        """
        try:
            produto = Produto.objects.get(id=pk)
            produto_nome = produto.nome
            produto.delete()
            return Response({
                'mensagem': f'Produto "{produto_nome}" removido com sucesso'
            }, status=status.HTTP_200_OK)
        except Produto.DoesNotExist:
            return Response({
                'erro': 'Produto não encontrado'
            }, status=status.HTTP_404_NOT_FOUND)
    
    @action(detail=False, methods=['get'], url_path='buscar')
    def buscar(self, request):
        """
        Rota de busca por nome ou marca
        """
        nome = request.query_params.get('nome', '')
        marca = request.query_params.get('marca', '')
        
        queryset = Produto.objects.all()
        
        if nome:
            queryset = queryset.filter(nome__icontains=nome)
        if marca:
            queryset = queryset.filter(marca__icontains=marca)
        
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)