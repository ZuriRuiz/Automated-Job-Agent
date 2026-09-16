
# ============================================================
# EMAIL SENDER
# ============================================================

import os
import smtplib

from email.message import EmailMessage


# ============================================================
# CONFIGURATION
# ============================================================

SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 465


# ============================================================
# SEND EMAIL
# ============================================================

def send_email(
    recipient,
    subject,
    body
):

    sender = os.environ["EMAIL_USERNAME"]
    password = os.environ["EMAIL_APP_PASSWORD"]

    message = EmailMessage()

    message["From"] = sender
    message["To"] = recipient
    message["Subject"] = subject

    message.set_content(
        body
    )

    with smtplib.SMTP_SSL(
        SMTP_SERVER,
        SMTP_PORT
    ) as server:

        server.login(
            sender,
            password
        )

        server.send_message(
            message
        )


# ============================================================
# REAL EMAIL TEST
# ============================================================

if __name__ == "__main__":

    print(
        "\n=============================="
    )

    print(
        "REAL EMAIL TEST"
    )

    print(
        "=============================="
    )

    recipient = os.environ["TEST_RECIPIENT"]

    send_email(
        recipient,
        "🤖 ZuriBot 2000™ - Test Email",
        """Hola Menors,

Este es un correo de prueba enviado automáticamente por ZuriBot 2000™ 🤖

Si estás leyendo esto, significa que:

✅ GitHub Actions puede autenticarse con Gmail.
✅ ZuriBot puede enviar correos.
✅ El sistema de email está funcionando correctamente.

Vamos que se puede. 💪❤️

Zuri ❤️
"""
    )

    print(
        "\nEmail sent successfully."
    )

