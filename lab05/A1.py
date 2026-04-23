import os
import smtplib
import time
from dotenv import load_dotenv
from email.mime.text import MIMEText
load_dotenv()

username = os.getenv("MAILTRAP_USER") or ""
password = os.getenv("MAILTRAP_PASSWORD") or ""


def send_mail(smtp, to_addr : str, format: str, body: str):
    if format == "txt":
        msg = MIMEText(body, "plain")
    elif format == "html":
        msg = MIMEText(f"<h1>{body}</h1>", "html")
    else:
        raise NotImplementedError("Unsupported format")
    msg["Subject"] = "Test email"
    msg["From"] = username
    msg["To"] = to_addr
    smtp.sendmail(username, to_addr, msg.as_string())


if __name__ == "__main__":
    smtp = smtplib.SMTP("sandbox.smtp.mailtrap.io", 2525)
    smtp.login(username, password)
    send_mail(smtp=smtp, to_addr="recipient@example.com", format="txt", body="Hello, this is a test email in txt!")
    time.sleep(10)
    send_mail(smtp=smtp, to_addr="recipient@example.com", format="html", body="Hello, this is a test email in html format!")
    smtp.quit()