# usuarios/utils.py - ADICIONE ESTA FUNÇÃO
import os
from django.core.mail import send_mail
from django.conf import settings

def enviar_email_recuperacao(email_destino, token, nome_usuario):
    """
    Envia e-mail de recuperação de senha
    """
    assunto = "Recuperação de Senha - Seu Sistema"
    
    # URL para redefinir senha (ajuste conforme sua configuração)
    url_base = os.getenv('FRONTEND_URL', 'http://localhost:3000')
    link_recuperacao = f"{url_base}/redefinir-senha?token={token}&email={email_destino}"
    
    mensagem = f"""
    Olá {nome_usuario},
    
    Você solicitou a recuperação de senha para sua conta.
    
    Clique no link abaixo para redefinir sua senha:
    {link_recuperacao}
    
    Este link expira em 1 hora.
    
    Se você não solicitou esta recuperação, ignore este e-mail.
    
    Atenciosamente,
    Equipe do Sistema
    """
    
    # Em produção, use:
    # send_mail(
    #     assunto,
    #     mensagem,
    #     settings.DEFAULT_FROM_EMAIL,
    #     [email_destino],
    #     fail_silently=False,
    # )
    
    # Para desenvolvimento, apenas imprime
    print(f"\n=== E-MAIL DE RECUPERAÇÃO (DESENVOLVIMENTO) ===")
    print(f"Para: {email_destino}")
    print(f"Assunto: {assunto}")
    print(f"Mensagem: {mensagem}")
    print("=" * 50)
    
    return True