import asyncio
import logging
import uuid
import datetime
from typing import List, Optional
from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel, EmailStr
from app.core.config import settings
from app.services.email_service import (
    send_test_notification_email,
    get_formatted_timestamps,
    get_email_catalog,
    async_dispatch_email_by_type,
    dispatch_email_by_type,
)
from app.services.supabase_email_templates import get_all_supabase_templates

logger = logging.getLogger(__name__)
router = APIRouter()

class UniversalEmailRequest(BaseModel):
    email: EmailStr
    type: str
    extra: Optional[dict] = None
    provider: Optional[str] = "auto" # "auto" | "supabase" | "smtp"

class BatchEmailRequest(BaseModel):
    email: Optional[EmailStr] = None

class NotificationItemModel(BaseModel):
    id: str
    type: str # "success" | "info" | "warning" | "alert"
    title: str
    message: str
    time: str
    read: bool
    href: str
    tag: Optional[str] = None

class TestNotificationRequest(BaseModel):
    email: Optional[EmailStr] = None
    channel: Optional[str] = "Email"

class AlertRuleModel(BaseModel):
    id: str
    event: str
    email: bool
    inApp: bool
    sms: bool

class NotificationPreferences(BaseModel):
    channels: dict
    jobAlerts: List[dict]
    teamAlerts: List[dict]
    frequency: str
    quietHours: bool
    quietStart: str
    quietEnd: str

# In-memory storage for notification items and settings
_notifications: List[dict] = [
    {
        "id": "notif-1",
        "type": "success",
        "title": "Job SR_v2_20240521 Completed",
        "message": "Super-resolution ×4 completed (2.5 m/pixel) for Ladakh Border Infrastructure.",
        "time": "5m ago",
        "read": False,
        "href": "/comparison?job=SR_v2_20240520_1030",
        "tag": "Processing",
    },
    {
        "id": "notif-2",
        "type": "info",
        "title": "GPU Worker Cluster Allocation",
        "message": "High-priority queue active. 4x A100 GPUs assigned to regional satellite batch.",
        "time": "24m ago",
        "read": False,
        "href": "/queue",
        "tag": "Compute",
    },
    {
        "id": "notif-3",
        "type": "warning",
        "title": "Cloud Cover Threshold Alert",
        "message": "Scene B02/B04 detected 18% cloud cover. Auto-masking applied successfully.",
        "time": "1h ago",
        "read": False,
        "href": "/validation?job=SR_v2_20240520_1030",
        "tag": "Preprocessing",
    },
    {
        "id": "notif-4",
        "type": "success",
        "title": "Validation Report Ready",
        "message": "Quality validation report exported (PSNR: 34.2 dB, SSIM: 0.892).",
        "time": "3h ago",
        "read": True,
        "href": "/validation?job=SR_v2_20240520_1030",
        "tag": "Reports",
    },
    {
        "id": "notif-5",
        "type": "alert",
        "title": "Storage Usage Warning",
        "message": "2.41 TB of 10.0 TB consumed. 48 satellite jobs currently archived.",
        "time": "1d ago",
        "read": True,
        "href": "/settings",
        "tag": "System",
    },
]

_preferences = {
    "channels": {"email": True, "inApp": True, "sms": False},
    "jobAlerts": [
        {"id": "job_completed", "event": "Job completed successfully", "email": True, "inApp": True, "sms": False},
        {"id": "job_failed", "event": "Job failed or timed out", "email": True, "inApp": True, "sms": True},
        {"id": "cloud_cover", "event": "Cloud cover exceeds threshold", "email": False, "inApp": True, "sms": False},
        {"id": "validation_ready", "event": "Validation metrics ready", "email": True, "inApp": True, "sms": False},
    ],
    "teamAlerts": [
        {"id": "member_joined", "event": "New analyst joined team", "email": True, "inApp": True, "sms": False},
        {"id": "quota_warning", "event": "Monthly compute quota at 80%", "email": True, "inApp": True, "sms": True},
    ],
    "frequency": "Real-time",
    "quietHours": True,
    "quietStart": "10:00 PM",
    "quietEnd": "07:00 AM",
}


def add_in_app_notification(item: dict) -> None:
    """Helper to prepend an event notification to the feed."""
    _notifications.insert(0, item)
    if len(_notifications) > 50:
        _notifications.pop()


@router.get("/notifications", response_model=List[NotificationItemModel])
async def list_notifications():
    return _notifications


@router.post("/notifications/read-all")
async def mark_all_read():
    for item in _notifications:
        item["read"] = True
    return {"status": "ok", "message": "All notifications marked as read"}


@router.post("/notifications/{item_id}/read")
async def mark_read(item_id: str):
    found = False
    for item in _notifications:
        if item["id"] == item_id:
            item["read"] = True
            found = True
            break
    if not found:
        raise HTTPException(status_code=404, detail="Notification not found")
    return {"status": "ok"}


@router.delete("/notifications/{item_id}")
async def dismiss_notification(item_id: str):
    global _notifications
    _notifications = [n for n in _notifications if n["id"] != item_id]
    return {"status": "ok"}


@router.post("/notifications/test")
async def send_test_notification(req: TestNotificationRequest, background_tasks: BackgroundTasks):
    target_email = req.email or settings.SMTP_FROM_EMAIL or "bhudhristi@gmail.com"
    channel = req.channel or "Email"

    try:
        # Run SMTP dispatch in threadpool so it does not block event loop
        await asyncio.to_thread(send_test_notification_email, target_email, channel)
    except Exception as exc:
        logger.exception("test_smtp_notification_failed", extra={"email": target_email, "error": str(exc)})
        raise HTTPException(status_code=502, detail=f"SMTP dispatch failed: {str(exc)}")

    # Add in-app confirmation
    utc_str, ist_str = get_formatted_timestamps()
    add_in_app_notification({
        "id": f"notif-test-{uuid.uuid4().hex[:6]}",
        "type": "success",
        "title": "SMTP Test Notification Dispatched",
        "message": f"Verified live test message delivered to {target_email} via {settings.SMTP_HOST}.",
        "time": "Just now",
        "read": False,
        "href": "/settings",
        "tag": "SMTP",
    })

    return {
        "status": "success",
        "message": f"Test notification sent to {target_email} via SMTP ({settings.SMTP_HOST})",
        "timestamp": ist_str,
    }


@router.get("/notifications/settings")
async def get_notification_settings():
    return _preferences


@router.put("/notifications/settings")
async def update_notification_settings(body: dict):
    _preferences.update(body)
    return {"status": "ok", "preferences": _preferences}


@router.get("/notifications/email/catalog")
async def list_email_catalog():
    """
    Returns the comprehensive catalog of all 18 Bhu-Dristi email types with metadata,
    sample payloads, and Supabase / SMTP delivery capabilities.
    """
    return {
        "total": 18,
        "smtp_server": settings.effective_smtp_host,
        "smtp_port": settings.effective_smtp_port,
        "smtp_user": settings.effective_smtp_user,
        "supabase_configured": bool(settings.SUPABASE_URL and "PROJECT_REF" not in settings.SUPABASE_URL),
        "types": get_email_catalog(),
    }


@router.get("/notifications/email/supabase-templates")
async def list_supabase_templates():
    """
    Returns copy-paste ready HTML email templates for Supabase Dashboard (Auth -> Email Templates).
    """
    return get_all_supabase_templates()


@router.post("/notifications/email/send-type")
async def send_email_by_type(payload: UniversalEmailRequest):
    """
    Universal email dispatch endpoint. Routes any of the 18 platform email types
    either via Supabase Auth (when applicable & configured) or direct SMTP relay.
    """
    try:
        res = await async_dispatch_email_by_type(
            email=str(payload.email),
            email_type=payload.type,
            extra=payload.extra,
            provider=payload.provider or "auto",
        )
        return res
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as exc:
        logger.exception("send_email_by_type_failed", extra={"email": payload.email, "type": payload.type, "error": str(exc)})
        raise HTTPException(status_code=502, detail=f"Email dispatch failed: {str(exc)}")


@router.post("/notifications/email/send-all-samples")
async def send_all_sample_emails_endpoint(payload: BatchEmailRequest, background_tasks: BackgroundTasks):
    """
    Dispatches all 18 sample emails to the target email address.
    """
    target = str(payload.email or settings.effective_smtp_from or "bhudhristi@gmail.com")
    catalog = get_email_catalog()

    async def _runner():
        for item in catalog:
            t = item["id"]
            try:
                await async_dispatch_email_by_type(target, t, item.get("sample_extra"))
                await asyncio.sleep(0.5)
            except Exception as e:
                logger.warning(f"Batch sample dispatch failed for {t}: {e}")

    background_tasks.add_task(_runner)
    return {
        "status": "queued",
        "recipient": target,
        "total_dispatches": len(catalog),
        "message": f"Queued {len(catalog)} sample emails for delivery to {target}.",
    }

