import base64
import json
import smtplib
import ssl
from email.message import EmailMessage
from urllib.parse import urlencode
from urllib.request import Request, urlopen


def email_report(sender: str, recipient: str, subject: str, body: str) -> EmailMessage:
    """Construct a previewable message; does not send."""
    message = EmailMessage()
    message["From"], message["To"], message["Subject"] = sender, recipient, subject
    message.set_content(body)
    return message


def send_email(
    message: EmailMessage,
    host: str,
    *,
    port: int = 465,
    username: str,
    password: str,
    timeout: float = 20,
) -> None:
    if timeout <= 0:
        raise ValueError("timeout must be positive")
    with smtplib.SMTP_SSL(
        host, port, timeout=timeout, context=ssl.create_default_context()
    ) as smtp:
        smtp.login(username, password)
        smtp.send_message(message)


def send_webhook(url: str, payload: dict, *, event_id: str, timeout: float = 20) -> int:
    """One delivery attempt; stable event ID lets a cooperating receiver deduplicate retries."""
    if not url.startswith("https://") or not event_id or timeout <= 0:
        raise ValueError("HTTPS URL, event_id and positive timeout required")
    request = Request(
        url,
        data=json.dumps(payload, allow_nan=False).encode(),
        headers={"Content-Type": "application/json", "Idempotency-Key": event_id},
    )
    with urlopen(request, timeout=timeout) as response:
        return response.status


def send_sms(
    body: str, recipient: str, sender: str, *, account_sid: str, token: str, timeout: float = 20
) -> str:
    """Explicit Twilio delivery; account credentials and a provisioned sender are required."""
    import re

    if not re.fullmatch(r"AC[a-fA-F0-9]{32}", account_sid) or not body or timeout <= 0:
        raise ValueError("valid account SID, message and positive timeout required")
    credentials = base64.b64encode(f"{account_sid}:{token}".encode()).decode()
    request = Request(
        f"https://api.twilio.com/2010-04-01/Accounts/{account_sid}/Messages.json",
        data=urlencode({"To": recipient, "From": sender, "Body": body}).encode(),
        headers={"Authorization": "Basic " + credentials},
    )
    with urlopen(request, timeout=timeout) as response:
        return json.load(response)["sid"]
