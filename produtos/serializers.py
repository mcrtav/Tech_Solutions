# produtos/serializers.py
from rest_framework import serializers
from produtos.models import Produto

class ProdutoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Produto
        fields = ["id", "nome", "descricao", "preco", "marca", "criado", "atualizado"]
        read_only_fields = ["id", "criado", "atualizado"]

    def validate_nome(self, value):
        value = value.strip()
        if len(value) < 3:
            raise serializers.ValidationError("Nome deve ter no mínimo 3 caracteres")
        return value

    def validate_preco(self, value):
        if value <= 0:
            raise serializers.ValidationError(
                "O valor não pode ser menor ou igual a zero."
            )
        return value

    def validate_marca(self, value):
        value = value.strip()
        if len(value) < 2:
            raise serializers.ValidationError(
                "A marca não pode ter menos que 2 caracteres."
            )
        return value

    def validate_descricao(self, value):
        value = value.strip()
        if len(value) < 10:
            raise serializers.ValidationError("A descrição deve ter pelo menos 10 caracteres.")
        return value