"""SMTP email sender for delivering .md files as attachments."""

from __future__ import annotations

import logging
import smtplib
from email.message import EmailMessage

from app.config import get_settings

log = logging.getLogger(__name__)


def send_markdown(*, to: str, subject: str, body: str, attachment: str, filename: str) -> None:
    settings = get_settings()
    msg = EmailMessage()
    msg["From"] = f"{settings.mail_from_name} <{settings.mail_from_address}>"
    msg["To"] = to
    msg["Subject"] = subject
    msg.set_content(body)
    msg.add_attachment(
        attachment.encode("utf-8"),
        maintype="text",
        subtype="markdown",
        filename=filename,
    )

    with smtplib.SMTP(settings.mail_host, settings.mail_port) as smtp:
        smtp.ehlo()
        if settings.mail_starttls:
            smtp.starttls()
            smtp.ehlo()
        if settings.mail_user and settings.mail_password:
            smtp.login(settings.mail_user, settings.mail_password)
        smtp.send_message(msg)
    log.info("email sent to %s (subject=%r)", to, subject)
