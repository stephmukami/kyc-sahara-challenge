from fastapi import APIRouter, Depends, Request
from fastapi.responses import Response
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.services import auth_service

router = APIRouter(prefix="/telephony/voice", tags=["telephony:voice"])

_XML_MEDIA_TYPE = "application/xml"


def _xml(body: str) -> Response:
    return Response(content=f"<Response>{body}</Response>", media_type=_XML_MEDIA_TYPE)


@router.post("/inbound")
async def inbound_call(request: Request) -> Response:
    """Africa's Talking hits this when an inbound call starts. The caller's
    number (from caller ID) is treated as proof of phone ownership — no OTP
    is needed for a voice signup, unlike the text/app signup flow."""
    await request.form()  # sessionId/callerNumber not needed at this step

    callback_url = str(request.url_for("recording_callback"))
    return _xml(
        "<Say>Welcome. After the beep, please say your full name, then press hash.</Say>"
        f'<Record finishOnKey="#" maxLength="10" trimSilence="true" playBeep="true" '
        f'callbackUrl="{callback_url}"/>'
    )


@router.post("/recording", name="recording_callback")
async def recording_callback(
    request: Request, db: AsyncSession = Depends(get_db)
) -> Response:
    form = await request.form()
    caller_number = str(form.get("callerNumber", ""))
    recording_url = str(form.get("recordingUrl", ""))

    if not caller_number or not recording_url:
        return _xml("<Say>Sorry, something went wrong. Please try again later.</Say>")

    await auth_service.complete_voice_signup(
        db, phone_number=caller_number, recording_url=recording_url
    )
    return _xml("<Say>Thank you. You are now signed up.</Say>")
