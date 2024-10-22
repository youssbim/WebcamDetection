import imghdr
import os
import smtplib
from email.message import EmailMessage

PASSWORD = os.getenv("PASSWORD") # Change with your email password token
SENDER = "sender@gmail.com"  # Change with sender email
RECEIVER = "sender@email.com" # Change with receiver email


def send_email(image_path):
    email_message = EmailMessage()
    email_message["Subject"] = "New customer showed up!"
    email_message.set_content("Hi, we spotted a new customer")

    with open(image_path, "rb") as file:
        content = file.read()
    email_message.add_attachment(content, maintype="image",
                                 subtype=imghdr.what(None, content))

    gmail = smtplib.SMTP("smtp.gmail.com", 587)
    gmail.ehlo()
    gmail.starttls()
    gmail.login(SENDER, PASSWORD)
    gmail.sendmail(SENDER, RECEIVER, email_message.as_string())
    gmail.quit()