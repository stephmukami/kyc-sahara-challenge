import logging

from app.core.config import get_settings
from app.services.providers.telephony.base import TelephonyProvider

settings = get_settings()
logger = logging.getLogger(__name__)


class ConsoleTelephonyProvider:
    """Fallback used when Africa's Talking isn't configured (local dev/tests)."""

    def send_otp(self, phone_number: str, code: str) -> None:
        logger.warning("OTP for %s: %s (no telephony provider configured)", phone_number, code)


class AfricasTalkingTelephonyProvider:
    def __init__(self) -> None:
        import africastalking

        africastalking.initialize(settings.africastalking_username, settings.africastalking_api_key)
        self._sms = africastalking.SMS

    def send_otp(self, phone_number: str, code: str) -> None:
        message = f"Your verification code is {code}. It expires in {settings.otp_ttl_minutes} minutes."
        self._sms.send(message, [phone_number], sender_id=settings.africastalking_sender_id)


def get_telephony_provider() -> TelephonyProvider:
    if settings.africastalking_username and settings.africastalking_api_key:
        return AfricasTalkingTelephonyProvider()
    return ConsoleTelephonyProvider()
