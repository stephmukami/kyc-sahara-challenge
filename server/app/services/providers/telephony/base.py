from typing import Protocol


class TelephonyProvider(Protocol):
    def send_otp(self, phone_number: str, code: str) -> None: ...
