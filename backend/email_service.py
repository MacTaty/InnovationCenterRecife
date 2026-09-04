import logging
import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

DESTINATARIO = "philippe.fontes@accenture.com"
CC = "carla.b.nascimento@accenture.com"
SMTP_HOST = "smtp.office365.com"
SMTP_PORT = 587


def enviar_email_experiencia(dados: dict) -> None:
    """
    Envia o formulário "Planeje uma experiência" por e-mail.

    dados deve conter: nome, empresa, email, mensagem.

    From:     conta fixa lida de EMAIL_REMETENTE (env)
    To:       DESTINATARIO fixo
    CC:       CC fixo
    Reply-To: e-mail do visitante — para resposta direta
    """
    remetente = os.environ["EMAIL_REMETENTE"]
    senha = os.environ["EMAIL_SENHA"]

    msg = MIMEMultipart()
    msg["From"] = remetente
    msg["To"] = DESTINATARIO
    msg["Cc"] = CC
    msg["Reply-To"] = dados["email"]
    msg["Subject"] = f"Innovation Center Recife — {dados['empresa']}"

    corpo = (
        f"Nome: {dados['nome']}\n"
        f"Empresa: {dados['empresa']}\n"
        f"E-mail para contato: {dados['email']}\n\n"
        f"O que quer explorar:\n{dados['mensagem']}"
    )
    msg.attach(MIMEText(corpo, "plain", "utf-8"))

    with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as smtp:
        smtp.ehlo()
        smtp.starttls()
        smtp.login(remetente, senha)
        smtp.sendmail(remetente, [DESTINATARIO, CC], msg.as_string())

    logging.info("E-mail enviado para %s (CC: %s)", DESTINATARIO, CC)
