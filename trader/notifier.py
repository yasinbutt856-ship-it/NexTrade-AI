from typing import Optional
from email.mime.text import MIMEText
import smtplib
from shared.logger import get_logger

logger = get_logger(__name__)


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
