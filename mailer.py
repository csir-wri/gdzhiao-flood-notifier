"""GMail mailing module."""

import enum
import smtplib
import ssl
from email.mime.text import MIMEText
from email.utils import formataddr

SSL_PORT = 465


class LoginResult(enum.IntEnum):
    """Indicates the result of a login operation.

    Args:
        enum (IntEnum): Login result.
    """

    Success = 0
    InvalidCredentials = 1
    OtherError = 2


# pylint: disable=invalid-name
# pylint: disable=global-statement
_server: smtplib.SMTP_SSL | None = None
_account = ""


def initialize():
    """Initializes the mailer module"""
    # TODO: Find a way to change the SMTP host if the address is not Gmail
    global _server
    _server = smtplib.SMTP_SSL("smtp.gmail.com", SSL_PORT, context=ssl.create_default_context())
    ## _server.login("mifmass.alerts@gmail.com", "flood-alerts")

    return _server


def login(address, password):
    """Logs in to the mail address for dispatching emails to recipients."""
    try:
        (_server or initialize()).login(address, password)
        global _account
        _account = address
        return LoginResult.Success
    except smtplib.SMTPAuthenticationError:
        return LoginResult.InvalidCredentials
    except (smtplib.SMTPHeloError, smtplib.SMTPNotSupportedError, smtplib.SMTPException):
        return LoginResult.OtherError


def send_mail(recipient_address, body_text):
    """Sends an email to the specified recipient.

    Args:
        recipient_address (str): Email address of the recipient.
        body_text (str): Text to be sent to the recipient.
    """

    # use MIMEText to compose the email content
    message = MIMEText(f"<pre>{body_text}</pre>", "html", "utf-8")
    message["From"] = formataddr(("GDZHIAO Flood Forecasting System Alert", _account))
    message["To"] = ", ".join(recipient_address)
    message["Subject"] = "GFFS Alert"

    if _server:
        _server.sendmail(_account, recipient_address, message.as_string())


def logout():
    """Closes the mailer account."""

    global _server
    if _server:
        _server.close()
    _server = None
