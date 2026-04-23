import os
import time
import base64
from socket import socket, AF_INET, SOCK_STREAM
from dotenv import load_dotenv
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage
load_dotenv()

username = os.getenv("MAILTRAP_USER") or ""
password = os.getenv("MAILTRAP_PASSWORD") or ""


def send_mail(mail_socket, to_addr : str, format: str, body: str, image_path: str):
    if format == "txt":
        text_msg = MIMEText(body, "plain")
    elif format == "html":
        text_msg = MIMEText(f"<h1>{body}</h1>", "html")
    else:
        raise NotImplementedError("Unsupported format")
    with open(image_path, "rb") as f:
        image = f.read()
    image_msg = MIMEImage(image)
    msg = MIMEMultipart()
    msg.attach(text_msg)
    msg.attach(image_msg)
    msg["Subject"] = "Test email"
    msg["From"] = username
    msg["To"] = to_addr

    mail_socket.send(b"MAIL FROM:<" + username.encode() + b">\r\n")
    response = mail_socket.recv(1024)
    if not response.startswith(b"250"):
        print("MAIL FROM command failed")
        return
    mail_socket.send(b"RCPT TO:<" + to_addr.encode() + b">\r\n")
    response = mail_socket.recv(1024)
    if not response.startswith(b"250"):
        print("RCPT TO command failed")
        return
    mail_socket.send(b"DATA\r\n")
    response = mail_socket.recv(1024)
    if not response.startswith(b"354"):
        print("DATA command failed")
        return
    mail_socket.send(msg.as_string().encode() + b"\r\n.\r\n")
    response = mail_socket.recv(1024)
    if response.startswith(b"250"):
        print("Email sent successfully")
    else:
        print("Failed to send email")


if __name__ == "__main__":
    mail_socket = socket(AF_INET, SOCK_STREAM)
    mail_socket.connect(("sandbox.smtp.mailtrap.io", 2525))

    response = mail_socket.recv(1024)
    if response.startswith(b"220"):
        print("Connected to SMTP server successfully")
    else:
        print("Failed to connect to SMTP server")
        mail_socket.close()
        exit(1)
    
    mail_socket.send(b"HELO localhost\r\n")
    response = mail_socket.recv(1024)
    if response.startswith(b"250"):
        print("SMTP server responded to HELO command successfully")
    else:
        print("SMTP server did not respond to HELO command")
        mail_socket.close()
        exit(1)
    
    mail_socket.send(b"AUTH LOGIN\r\n")
    response = mail_socket.recv(1024)
    if response.startswith(b"334"):
        print("SMTP server is ready for authentication")
    else:
        print("SMTP server is not ready for authentication")
        mail_socket.close()
        exit(1)

    mail_socket.send(base64.b64encode(username.encode()) + b"\r\n")
    response = mail_socket.recv(1024)
    if response.startswith(b"334"):
        print("Username accepted, waiting for password")
    else:
        print("Username rejected by SMTP server")
        mail_socket.close()
        exit(1)
    mail_socket.send(base64.b64encode(password.encode()) + b"\r\n")
    response = mail_socket.recv(1024)
    if response.startswith(b"235"):
        print("Authentication successful")
    else:
        print("Authentication failed")
        mail_socket.close()
        exit(1)

    send_mail(mail_socket=mail_socket, to_addr="recipient@example.com", format="txt", body="Hello, this is a test email in txt format with image!", image_path="img/lena.png")
    time.sleep(10)
    send_mail(mail_socket=mail_socket, to_addr="recipient@example.com", format="html", body="Hello, this is a test email in html format with image!", image_path="img/lena.png")
    mail_socket.send(b"QUIT\r\n")
    mail_socket.close()