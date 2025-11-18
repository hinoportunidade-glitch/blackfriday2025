import os
import smtplib
from email.message import EmailMessage
from dotenv import load_dotenv

load_dotenv()

def send_alert(mensagem):
    # Configurações do seu e-mail (Gmail, Hotmail, etc.)
    EMAIL = os.getenv("MEU_EMAIL")          # seu e-mail completo
    SENHA = os.getenv("SENHA_EMAIL")        # senha de app (explico já já)
    
    msg = EmailMessage()
    msg['Subject'] = 'BLACK FRIDAY ALERTA - PREÇO BAIXOU!'
    msg['From'] = EMAIL
    msg['To'] = EMAIL                              # envia pra você mesmo
    msg.set_content(mensagem)

    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) if 'gmail' in EMAIL else \
             smtplib.SMTP('smtp-mail.outlook.com', 587) if 'outlook' in EMAIL or 'hotmail' in EMAIL else \
             smtplib.SMTP('smtp.yahoo.com', 587):
            server = smtplib.SMTP_SSL('smtp.gmail.com', 465) if 'gmail' in EMAIL else \
                     smtplib.SMTP('smtp-mail.outlook.com', 587) if 'outlook' in EMAIL or 'hotmail' in EMAIL else None
            if not 'gmail' in EMAIL:
                server.starttls()
            server.login(EMAIL, SENHA)
            server.send_message(msg)
            print("E-MAIL ENVIADO COM SUCESSO!")
    except Exception as e:
        print("Erro ao enviar e-mail:", e)
