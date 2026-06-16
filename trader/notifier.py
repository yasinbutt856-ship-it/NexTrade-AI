from typing import Optional
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import smtplib
from pathlib import Path
from shared.logger import get_logger

logger = get_logger(__name__)

TEMPLATES_DIR = Path(__file__).parent / "templates"

def _load_template(name: str) -> str:
    path = TEMPLATES_DIR / name
    if path.exists():
        return path.read_text(encoding="utf-8")
    return ""

def _render_template(template: str, **kwargs) -> str:
    result = template
    for key, val in kwargs.items():
        result = result.replace("{{" + key + "}}", str(val) if val is not None else "")
    import re
    result = re.sub(r"\{\{#(\w+)\}}(.*?)\{\{/\1\}}", lambda m: m.group(2) if kwargs.get(m.group(1)) else "", result, flags=re.DOTALL)
    return result


class Notifier:
    def __init__(
        self,
        telegram_token: Optional[str] = None,
        telegram_chat_id: Optional[str] = None,
        smtp_host: Optional[str] = None,
        smtp_port: Optional[int] = None,
        smtp_user: Optional[str] = None,
        smtp_password: Optional[str] = None,
        email_from: Optional[str] = None,
        email_to: Optional[str] = None,
    ):
        self.telegram_token = telegram_token
        self.telegram_chat_id = telegram_chat_id
        self.smtp_host = smtp_host
        self.smtp_port = smtp_port
        self.smtp_user = smtp_user
        self.smtp_password = smtp_password
        self.email_from = email_from
        self.email_to = email_to
        self._telegram_enabled = bool(telegram_token and telegram_chat_id)
        self._email_enabled = bool(
            smtp_host and smtp_user and smtp_password and email_from and email_to
        )

    async def send_trade_notification(
        self,
        symbol: str,
        action: str,
        price: float,
        quantity: float,
        pnl: Optional[float] = None,
    ) -> None:
        message = self._format_trade_message(symbol, action, price, quantity, pnl)
        await self._send_all(message)

    async def send_alert(self, message: str) -> None:
        await self._send_all(f"⚠️ Alert: {message}")

    async def send_error(self, error: str) -> None:
        await self._send_all(f"🚨 Error: {error}")

    def _format_trade_message(
        self, symbol: str, action: str, price: float, quantity: float, pnl: Optional[float]
    ) -> str:
        msg = (
            f"💰 *Trade Executed*\n"
            f"Symbol: {symbol}\n"
            f"Action: {action.upper()}\n"
            f"Price: ${price:.4f}\n"
            f"Quantity: {quantity:.6f}\n"
        )
        if pnl is not None:
            emoji = "🟢" if pnl >= 0 else "🔴"
            msg += f"{emoji} P&L: ${pnl:.2f}"
        return msg

    async def _send_all(self, message: str) -> None:
        if self._telegram_enabled:
            try:
                await self._send_telegram(message)
            except Exception as e:
                logger.error("telegram_send_error", error=str(e))
        if self._email_enabled:
            try:
                await self._send_email(message)
            except Exception as e:
                logger.error("email_send_error", error=str(e))

    async def _send_telegram(self, message: str) -> None:
        import httpx

        url = f"https://api.telegram.org/bot{self.telegram_token}/sendMessage"
        payload = {
            "chat_id": self.telegram_chat_id,
            "text": message,
            "parse_mode": "Markdown",
        }
        async with httpx.AsyncClient(timeout=10) as client:
            response = await client.post(url, json=payload)
            response.raise_for_status()
        logger.debug("telegram_sent")

    async def send_custom_email(self, to: str, subject: str, body: str, html_template: str = "", **template_vars) -> None:
        if not self.smtp_host or not self.smtp_user or not self.smtp_password or not self.email_from:
            logger.warning("email_not_configured", to=to, subject=subject)
            return
        msg = MIMEMultipart("alternative") if html_template else MIMEText(body, "plain", "utf-8")
        msg["Subject"] = subject
        msg["From"] = self.email_from
        msg["To"] = to
        if isinstance(msg, MIMEMultipart):
            msg.attach(MIMEText(body, "plain", "utf-8"))
            html_body = _render_template(_load_template(html_template), **template_vars)
            if html_body:
                msg.attach(MIMEText(html_body, "html", "utf-8"))
        with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
            server.starttls()
            server.login(self.smtp_user, self.smtp_password)
            server.send_message(msg)
        logger.debug("custom_email_sent", to=to, subject=subject)

    async def _send_email(self, message: str) -> None:
        msg = MIMEText(message, "plain", "utf-8")
        msg["Subject"] = "Trading Bot Notification"
        msg["From"] = self.email_from
        msg["To"] = self.email_to

        with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
            server.starttls()
            server.login(self.smtp_user, self.smtp_password)
            server.send_message(msg)
        logger.debug("email_sent")
