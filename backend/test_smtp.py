import os
import sys
import datetime
from pathlib import Path
from dotenv import load_dotenv

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

# Ensure backend root is on sys.path
backend_dir = Path(__file__).resolve().parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

load_dotenv(backend_dir / ".env")

from app.core.config import settings
from app.services.email_service import (
    render_otp_email_html,
    render_otp_email_text,
    send_styled_otp_email,
)

print("=" * 60)
print("🛰️  भू DRISTI — SMTP & Styled Email Dispatch Diagnostic")
print("=" * 60)
print(f"SMTP Server: {settings.SMTP_HOST}:{settings.SMTP_PORT}")
print(f"User:        {settings.SMTP_USER}")
print(f"From Email:  {settings.SMTP_FROM_EMAIL}")
print("=" * 60)

test_code = "849201"
recipient = settings.SMTP_USER or "bhudhristi@gmail.com"

# 1. Generate & export an offline HTML preview
preview_file = backend_dir / "email_preview.html"
html_content = render_otp_email_html(recipient, test_code, purpose="login")
with open(preview_file, "w", encoding="utf-8") as f:
    f.write(html_content)
print(f"✅ Generated local HTML preview file: {preview_file}")

# 2. Dispatch real email via SMTP
print(f"\n📡 Dispatching Bhu-Dristi styled email with OTP [{test_code}] to {recipient}...")

try:
    send_styled_otp_email(email=recipient, code=test_code, purpose="login")
    print(f"\n🎉 SUCCESS: Bhu-Dristi styled verification email delivered successfully!")
    print(f"   Recipient: {recipient}")
    print(f"   Subject:   भू DRISTI — Verification Code [{test_code}]")
    print("   Check your inbox now to admire the new responsive satellite theme.\n")
except Exception as e:
    print(f"\n❌ ERROR: Failed to dispatch styled email.")
    print(f"Details: {e}")
    sys.exit(1)
