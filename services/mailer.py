import smtplib, ssl
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from settings import Mailer


async def send_email(data: str) -> any:
    # print(f"В Mailer пришли данные: {data}")
    msg = MIMEMultipart()
    msg['From'] = Mailer.sender
    msg['To'] = Mailer.send_to
    msg['Subject'] = Mailer.subject

    message = f"{Mailer.message_text}\n{data}"
    msg.attach(MIMEText(message, 'plain'))
    msg.add_header('reply-to', Mailer.sender)

    try:
        server = smtplib.SMTP_SSL(Mailer.smtp_server, Mailer.port)
        # server.set_debuglevel(1)
        server.ehlo()
        server.login(Mailer.username, Mailer.password)
        server.sendmail(msg['From'], msg['To'], msg.as_string())
        server.quit()
        print("Email sent successfully.")
        return "success"
    except smtplib.SMTPAuthenticationError as e:
        print(e)
        return e
