"""GMail mailing module."""


import smtplib
import ssl
SSL_PORT = 465

# pylint: disable=invalid-name
# pylint: disable=global-statement
_server = None


def initialize():
    """Initializes the mailer module
    """
    global _server
    # create a secure SSL context
    context = ssl.create_default_context()

    _server = smtplib.SMTP_SSL(
        "smtp.gmail.com", SSL_PORT, context=context)
    _server.login("mifmass.alerts@gmail.com", "flood-alerts")


def send_mail(recipient_address, body_text):
    """Sends an email to the specified recipient.

    Args:
        recipient_address (str): Email address of the recipient.
        body_text (str): Text to be sent to the recipient.
    """
    global _server
    _server.sendmail("mifmass.alerts@gmail.com",
                     recipient_address, body_text)


def close():
    """Closes the mailer account."""

    global _server
    _server.close()
    _server = None
