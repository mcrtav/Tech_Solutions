# usuarios/utils.py
import random
import string
import secrets

class GeradorSenha:
    """Classe utilitária para gerar e validar senhas fortes"""
    
    @staticmethod
    def gerar_senha_forte(tamanho=12):
        """
        Gera uma senha forte aleatória
        Requisitos: 1 maiúscula, 1 minúscula, 1 número, 1 especial
        """
        if tamanho < 8:
            tamanho = 8
        
        # Conjuntos de caracteres
        maiusculas = string.ascii_uppercase
        minusculas = string.ascii_lowercase
        numeros = string.digits
        especiais = '@$!%*?&'
        
        # Garantir pelo menos um de cada tipo
        senha = [
            random.choice(maiusculas),
            random.choice(minusculas),
            random.choice(numeros),
            random.choice(especiais)
        ]
        
        # Completar com caracteres aleatórios
        todos_caracteres = maiusculas + minusculas + numeros + especiais
        senha.extend(random.choices(todos_caracteres, k=tamanho-4))
        
        # Embaralhar a senha
        random.shuffle(senha)
        
        return ''.join(senha)
    
    @staticmethod
    def validar_forca_senha(senha):
        """
        Retorna um dicionário com análise da força da senha
        """
        resultado = {
            'tamanho_ok': len(senha) >= 8,
            'tem_maiuscula': any(c.isupper() for c in senha),
            'tem_minuscula': any(c.islower() for c in senha),
            'tem_numero': any(c.isdigit() for c in senha),
            'tem_especial': any(c in '@$!%*?&' for c in senha),
            'caracteres_validos': all(c in string.ascii_letters + string.digits + '@$!%*?&' for c in senha)
        }
        
        # Calcular força (0-100)
        pontos = 0
        if resultado['tamanho_ok']:
            pontos += 20
            if len(senha) >= 12:
                pontos += 10
        if resultado['tem_maiuscula']:
            pontos += 15
        if resultado['tem_minuscula']:
            pontos += 15
        if resultado['tem_numero']:
            pontos += 15
        if resultado['tem_especial']:
            pontos += 15
        if resultado['caracteres_validos']:
            pontos += 10
        
        resultado['pontuacao'] = pontos
        resultado['forca'] = 'Fraca' if pontos < 60 else 'Média' if pontos < 80 else 'Forte' if pontos < 95 else 'Muito Forte'
        
        return resultado
    
    @staticmethod
    def gerar_senha_memoravel(palavras=3):
        """
        Gera uma senha memorável usando palavras
        Exemplo: Gato@Azul!2024
        """
        palavras_comuns = [
            'gato', 'cachorro', 'casa', 'sol', 'lua', 'mar', 'rio', 'flor',
            'livro', 'mesa', 'cadeira', 'porta', 'janela', 'tempo', 'noite',
            'dia', 'verde', 'azul', 'vermelho', 'amarelo', 'branco', 'preto'
        ]
        
        # Selecionar palavras aleatórias
        palavras_escolhidas = random.sample(palavras_comuns, min(palavras, len(palavras_comuns)))
        
        # Capitalizar a primeira letra de cada palavra
        palavras_escolhidas = [p.capitalize() for p in palavras_escolhidas]
        
        # Adicionar caractere especial e número
        especiais = ['@', '$', '!', '%', '*', '?', '&']
        senha = ''.join(palavras_escolhidas)
        senha += random.choice(especiais)
        senha += str(random.randint(10, 99))
        
        return senha