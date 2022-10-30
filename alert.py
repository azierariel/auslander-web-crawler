import smtplib, ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os


def send_mail(url_form, url_turno):
    sender_email = os.environ.get("SENDER_EMAIL")
    receiver_email = os.environ.get("RECEIVER_EMAIL")
    message = """\
    Subject: Hi there

    This message is sent from Python."""

    port = 465  # For SSL
    smtp_server = "smtp.gmail.com"
    password = os.environ.get("EMAIL_PASSWORD")
    context = ssl.create_default_context()

    message = MIMEMultipart("alternative")
    message["Subject"] = "TURNOS AUSLANDER YA!!"
    message["From"] = sender_email
    message["To"] = receiver_email

    text = f"""\
    Gonzaa!!\n
    Podria haber turnos disponibles en Auslander!!!\n
    Pagina del formulario: {url_form}\n
    Pagina del turno: {url_turno} <<-- click aqui!\n
    Notas:\n
    \tPagina del formulario</i> es la pagina que refresco antes para ver si hay turnos.\n
    \tPagina del turno</i> es la pagina que viene si no recivo el mensaje de que no hay turnos (desconocida para mi).\n\n
    Su bot de confianza.
    """
    html = f"""\
    <html>

    <body>
        <p>Gonzaa!!<br>
            Podria haber turnos disponibles en Auslander!!!<br>
            <a href="{url_form}">Pagina del formulario</a><br>
            <a href="{url_turno}">Pagina del turno <<-- click aqui!</a>
            <p>Notas:</p>
            <a><i>Pagina del formulario</i> es la pagina que refresco antes para ver si hay turnos.</a><br>
                <a><i>Pagina del turno</i> es la pagina que viene si no recivo el mensaje de que no hay turnos (desconocida para mi).</a>
        </p><br>
        <p>Su bot de confianza.</p>
    </body>

    </html>
    """

    part1 = MIMEText(text, "plain")
    part2 = MIMEText(html, "html")

    message.attach(part1)
    message.attach(part2)
    with smtplib.SMTP_SSL(smtp_server, port, context=context) as server:
        server.login(sender_email, password)
        server.sendmail(sender_email, receiver_email.split(","), message.as_string())
