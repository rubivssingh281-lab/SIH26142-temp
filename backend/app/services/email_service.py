import datetime
import logging
import smtplib
from email.message import EmailMessage
from zoneinfo import ZoneInfo
from app.core.config import settings

logger = logging.getLogger(__name__)


def get_formatted_timestamps() -> tuple[str, str]:
    """
    Returns (utc_str, ist_str) for telemetry timestamps.
    """
    now_utc = datetime.datetime.now(datetime.timezone.utc)
    utc_str = now_utc.strftime("%d %b %Y, %H:%M:%S UTC")
    try:
        ist_zone = ZoneInfo("Asia/Kolkata")
        now_ist = now_utc.astimezone(ist_zone)
        ist_str = now_ist.strftime("%d %b %Y, %H:%M:%S IST")
    except Exception:
        ist_str = utc_str
    return utc_str, ist_str


def render_otp_email_html(email: str, code: str, purpose: str = "login") -> str:
    """
    Renders the exact Bhu-Dristi branded satellite email template matching the user's specification.
    """
    utc_str, ist_str = get_formatted_timestamps()
    clean_code = str(code).strip()
    digits = list(clean_code) if len(clean_code) == 6 else None

    if purpose == "login":
        purpose_tag = "VERIFICATION PASS · OPERATOR SIGN-IN"
        purpose_title = "Sign In to भू DRISTI"
        purpose_desc = (
            "A sign-in request was initiated for your registered account on the "
            "<strong>भू DRISTI</strong> geospatial intelligence platform. "
            "Authorize your terminal access using the single-use verification code below."
        )
        badge_bg = "#fef3c7"
        badge_color = "#92400e"
        badge_border = "#fde68a"
    else:
        purpose_tag = "ACCOUNT ACTIVATION · NEW USER"
        purpose_title = "Welcome to भू DRISTI"
        purpose_desc = (
            "Welcome to the <strong>भू DRISTI</strong> geospatial intelligence platform. "
            "To activate your workspace access and verify your account, "
            "enter the single-use verification code below."
        )
        badge_bg = "#e0f2fe"
        badge_color = "#075985"
        badge_border = "#bae6fd"

    # Render digit boxes for 6-digit codes
    if digits:
        digit_cells = "".join(
            f"""<td align="center" style="padding:0 4px">
                <div class="digit-box" style="width:48px;height:56px;line-height:56px;font-family:'SF Mono',Consolas,'Liberation Mono',Menlo,Monaco,monospace;font-size:32px;font-weight:800;color:#d6532b;background:#ffffff;border:2px solid #f97316;border-radius:10px;text-align:center">
                  {d}
                </div>
              </td>"""
            for d in digits
        )
        digit_table = f"""<table border="0" cellpadding="0" cellspacing="0" style="margin:0 auto">
            <tr>{digit_cells}</tr>
          </table>"""
    else:
        digit_table = f"""<div style="font-family:'SF Mono',Consolas,monospace;font-size:36px;font-weight:800;letter-spacing:10px;color:#d6532b;text-align:center">
            {clean_code}
          </div>"""

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <meta http-equiv="X-UA-Compatible" content="IE=edge">
  <title>भू DRISTI — Verification Code</title>
  <style>
    /* Client reset */
    body, table, td, a {{ -webkit-text-size-adjust: 100%; -ms-text-size-adjust: 100%; }}
    table, td {{ mso-table-lspace: 0pt; mso-table-rspace: 0pt; }}
    img {{ -ms-interpolation-mode: bicubic; border: 0; outline: none; text-decoration: none; }}
    body {{ margin: 0; padding: 0; width: 100% !important; min-width: 100%; background-color: #0E1626; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; color: #1E293B; }}

    /* Responsive */
    @media only screen and (max-width: 620px) {{
      .email-container {{ width: 100% !important; max-width: 100% !important; border-radius: 0 !important; }}
      .mobile-padding {{ padding-left: 20px !important; padding-right: 20px !important; }}
      .header-pad {{ padding: 28px 20px !important; }}
      .digit-box {{ width: 38px !important; height: 48px !important; line-height: 48px !important; font-size: 24px !important; border-radius: 8px !important; }}
      .meta-cell {{ display: block !important; width: 100% !important; margin-bottom: 12px !important; }}
    }}
  </style>
</head>
<body style="margin:0;padding:0;background-color:#0E1626;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,Helvetica,Arial,sans-serif;color:#1E293B;">

  <!-- Hidden Preview Text (Preheader) -->
  <div style="display:none;font-size:1px;color:#0E1626;line-height:1px;max-height:0px;max-width:0px;opacity:0;overflow:hidden;">
    Your भू DRISTI single-use verification code is {clean_code}. Valid for 10 minutes. National Geospatial Intelligence Platform.
  </div>

  <!-- Background Wrapper -->
  <table width="100%" border="0" cellpadding="0" cellspacing="0" style="background:radial-gradient(circle at 50% 0%,#1A2844 0%,#0E1626 70%);padding:36px 10px;">
    <tr>
      <td align="center">

        <!-- Outer Card Container -->
        <table class="email-container" width="600" border="0" cellpadding="0" cellspacing="0" style="width:600px;max-width:600px;background-color:#ffffff;border-radius:18px;overflow:hidden;box-shadow:0 16px 40px rgba(0,0,0,0.45),0 0 0 1px rgba(255,255,255,0.08);">

          <!-- 1. Satellite Top Bar -->
          <tr>
            <td style="background-color:#070b14;padding:12px 26px;border-bottom:1px solid rgba(255,255,255,0.08)">
              <table width="100%" border="0" cellpadding="0" cellspacing="0">
                <tr>
                  <td align="left" style="font-family:'SF Mono',Consolas,Monaco,monospace;font-size:11px;color:#94a3b8;letter-spacing:1.2px;text-transform:uppercase">
                    🛰️ NTRO · SIH 2026 · GEOSPATIAL INTELLIGENCE
                  </td>
                  <td align="right" style="font-family:'SF Mono',Consolas,Monaco,monospace;font-size:11px;color:#10b981;letter-spacing:1px;font-weight:bold">
                    ● SECURE TRANSMISSION
                  </td>
                </tr>
              </table>
            </td>
          </tr>

          <!-- 2. Hero Banner -->
          <tr>
            <td class="header-pad" style="background:linear-gradient(135deg,#091326 0%,#152540 30%,#8c2e12 70%,#d6532b 90%,#0f8c7f 100%);padding:36px 32px;color:#ffffff">
              <table width="100%" border="0" cellpadding="0" cellspacing="0">
                <tr>
                  <td>
                    <!-- Pill Tag -->
                    <div style="display:inline-block;padding:5px 13px;background:rgba(255,255,255,0.16);border:1px solid rgba(255,255,255,0.28);border-radius:20px;font-size:10.5px;font-weight:700;letter-spacing:1.4px;text-transform:uppercase;margin-bottom:14px">
                      ✨ NATIONAL GEOSPATIAL PLATFORM
                    </div>

                    <!-- Main Brand Headline -->
                    <table border="0" cellpadding="0" cellspacing="0">
                      <tr>
                        <td valign="middle" style="padding-right:14px">
                          <div style="width:44px;height:44px;background:linear-gradient(135deg,#f97316 0%,#d6532b 100%);border-radius:12px;text-align:center;line-height:44px;font-size:24px;border:1px solid rgba(255,255,255,0.3)">
                            🛰️
                          </div>
                        </td>
                        <td valign="middle">
                          <h1 style="margin:0;font-size:34px;font-weight:800;letter-spacing:-0.5px;line-height:1.1;color:#ffffff">
                            भू <span style="color:#fde047">DRISTI</span>
                          </h1>
                          <p style="margin:4px 0 0 0;font-size:13.5px;color:rgba(255,255,255,0.88);font-weight:500;letter-spacing:0.3px">
                            Earth Observation &amp; Geospatial Intelligence Workspace
                          </p>
                        </td>
                      </tr>
                    </table>
                  </td>
                </tr>
              </table>
            </td>
          </tr>

          <!-- 3. Card Body -->
          <tr>
            <td class="mobile-padding" style="padding:34px 34px 28px 34px;background-color:#ffffff">

              <!-- Purpose Badge & Header -->
              <table width="100%" border="0" cellpadding="0" cellspacing="0" style="margin-bottom:22px">
                <tr>
                  <td>
                    <div style="display:inline-block;background-color:{badge_bg};color:{badge_color};border:1px solid {badge_border};border-radius:6px;padding:4px 11px;font-size:11px;font-weight:800;text-transform:uppercase;letter-spacing:1px;margin-bottom:12px">
                      {purpose_tag}
                    </div>
                    <h2 style="margin:0 0 10px 0;font-size:22px;font-weight:800;color:#0f172a;letter-spacing:-0.4px">
                      {purpose_title}
                    </h2>
                    <p style="margin:0;font-size:14.5px;color:#475569;line-height:1.65">
                      {purpose_desc}
                    </p>
                  </td>
                </tr>
              </table>

              <!-- 4. Hero OTP Showcase Box -->
              <table width="100%" border="0" cellpadding="0" cellspacing="0" style="margin:26px 0;background:linear-gradient(180deg,#fffbf8 0%,#fff5ed 100%);border:2px dashed #ea580c;border-radius:16px;text-align:center">
                <tr>
                  <td style="padding:28px 18px 24px 18px">
                    <div style="font-family:'SF Mono',Consolas,monospace;font-size:11px;font-weight:700;letter-spacing:2px;text-transform:uppercase;color:#c2410c;margin-bottom:14px">
                      SINGLE-USE VERIFICATION CODE
                    </div>

                    <div style="margin:8px 0 14px 0">
                      {digit_table}
                    </div>

                    <div style="display:inline-block;margin-top:8px;background-color:#ffffff;border:1px solid #fed7aa;border-radius:20px;padding:6px 16px;font-size:12px;font-weight:700;color:#9a3412">
                      ⏱ Expires in 10 minutes &nbsp;·&nbsp; Single-use authorization code
                    </div>

                    <div style="margin-top:12px;font-size:12.5px;color:#64748b">
                      Enter this code in your भू DRISTI browser window to complete authentication.
                    </div>
                  </td>
                </tr>
              </table>

              <!-- 5. Session Details Grid -->
              <table width="100%" border="0" cellpadding="0" cellspacing="0" style="margin:22px 0;background-color:#f8fafc;border:1px solid #e2e8f0;border-radius:12px;padding:14px 16px">
                <tr>
                  <td>
                    <table width="100%" border="0" cellpadding="0" cellspacing="0">
                      <tr>
                        <td class="meta-cell" width="50%" valign="top" style="padding:6px 10px">
                          <div style="font-family:'SF Mono',Consolas,monospace;font-size:10.5px;text-transform:uppercase;letter-spacing:0.6px;color:#64748b;font-weight:700">
                            Authorized Account
                          </div>
                          <div style="font-size:13.5px;color:#0f172a;font-weight:700;word-break:break-all;margin-top:3px">
                            {email}
                          </div>
                        </td>
                        <td class="meta-cell" width="50%" valign="top" style="padding:6px 10px">
                          <div style="font-family:'SF Mono',Consolas,monospace;font-size:10.5px;text-transform:uppercase;letter-spacing:0.6px;color:#64748b;font-weight:700">
                            Timestamp (IST / UTC)
                          </div>
                          <div style="font-size:12.5px;color:#0f172a;font-weight:600;margin-top:3px">
                            {ist_str}
                          </div>
                          <div style="font-size:11px;color:#64748b;margin-top:1px">
                            ({utc_str})
                          </div>
                        </td>
                      </tr>
                      <tr>
                        <td class="meta-cell" width="50%" valign="top" style="padding:10px 10px 4px 10px">
                          <div style="font-family:'SF Mono',Consolas,monospace;font-size:10.5px;text-transform:uppercase;letter-spacing:0.6px;color:#64748b;font-weight:700">
                            Security Classification
                          </div>
                          <div style="font-size:13px;color:#0f8c7f;font-weight:700;margin-top:3px">
                            ● Restricted Workspace
                          </div>
                        </td>
                        <td class="meta-cell" width="50%" valign="top" style="padding:10px 10px 4px 10px">
                          <div style="font-family:'SF Mono',Consolas,monospace;font-size:10.5px;text-transform:uppercase;letter-spacing:0.6px;color:#64748b;font-weight:700">
                            Organization
                          </div>
                          <div style="font-size:13px;color:#0f172a;font-weight:600;margin-top:3px">
                            National Technical Research Organisation (NTRO)
                          </div>
                        </td>
                      </tr>
                    </table>
                  </td>
                </tr>
              </table>

              <!-- 6. Security Notice -->
              <table width="100%" border="0" cellpadding="0" cellspacing="0" style="margin-top:16px;background-color:#f0fdf4;border-left:4px solid #10b981;border-radius:6px;padding:14px 16px">
                <tr>
                  <td valign="top" width="24" style="padding-right:10px;font-size:16px">
                    🛡️
                  </td>
                  <td valign="top" style="font-size:12.5px;color:#166534;line-height:1.6">
                    <strong style="color:#14532d">Security Notice:</strong> Never forward or share this 6-digit verification code with anyone. भू DRISTI platform staff will never solicit this code. If you did not initiate this authentication request, you can safely ignore this email.
                  </td>
                </tr>
              </table>

            </td>
          </tr>

          <!-- 7. Footer -->
          <tr>
            <td class="mobile-padding" style="background-color:#070b14;padding:28px 32px;text-align:center;color:#94a3b8;border-top:1px solid rgba(255,255,255,0.08)">
              <table width="100%" border="0" cellpadding="0" cellspacing="0">
                <tr>
                  <td align="center">
                    <div style="font-size:14px;font-weight:700;color:#f1f5f9;letter-spacing:0.6px;margin-bottom:6px">
                      भू DRISTI — National Geospatial Intelligence Platform
                    </div>
                    <div style="font-size:11.5px;color:#64748b;line-height:1.55;max-width:480px;margin:0 auto">
                      National Technical Research Organisation (NTRO) · Smart India Hackathon
                    </div>
                    <div style="margin-top:14px;font-size:10.5px;color:#475569">
                      This is an automated system notification. Please do not reply directly to this email address.
                    </div>
                  </td>
                </tr>
              </table>
            </td>
          </tr>

        </table>

      </td>
    </tr>
  </table>

</body>
</html>
"""
    return html



def render_otp_email_text(email: str, code: str, purpose: str = "login") -> str:
    """
    High-fidelity scientific plain-text fallback for terminal clients and notifications.
    """
    utc_str, ist_str = get_formatted_timestamps()
    label = "OPERATOR LOGIN VERIFICATION" if purpose == "login" else "ACCOUNT WORKSPACE ACTIVATION"
    clean_code = str(code).strip()

    return (
        "======================================================================\n"
        "                  भू DRISTI — GEOSPATIAL INTELLIGENCE                \n"
        "       AI Super-Resolution Earth Observation System (NTRO PS-26142)  \n"
        "======================================================================\n\n"
        f"MISSION DIRECTIVE: {label}\n\n"
        "----------------------------------------------------------------------\n"
        "  SINGLE-USE VERIFICATION TOKEN:\n\n"
        f"               >>>   [  {clean_code}  ]   <<<\n\n"
        "  ⏱  VALIDITY: 10 MINUTES · SINGLE-USE AUTHORIZATION ONLY\n"
        "----------------------------------------------------------------------\n\n"
        "TELEMETRY DOSSIER:\n"
        f"  • Operator Account  : {email}\n"
        f"  • Timestamp (IST)   : {ist_str}\n"
        f"  • Timestamp (UTC)   : {utc_str}\n"
        "  • Security Level    : Restricted Geospatial Workspace (Level 2)\n"
        "  • Mission Pipeline  : 10m Multi-Spectral (B02-B08) ➔ 2.5m Analysis-Ready\n"
        "  • Cryptography      : TLS 1.3 / HMAC-SHA256 Multi-Factor Token\n\n"
        "SECURITY NOTICE (ZERO-TRUST PROTOCOL):\n"
        "  Never disclose or forward this verification code to anyone.\n"
        "  भू DRISTI operators and staff will NEVER ask for this token.\n"
        "  If you did not initiate this authentication sequence, ignore this message.\n\n"
        "======================================================================\n"
        "National Technical Research Organisation (NTRO) · Smart India Hackathon\n"
        "Deep Learning Super-Resolution from Medium-Resolution Imagery\n"
        "======================================================================\n"
    )


def send_styled_otp_email(email: str, code: str, purpose: str = "login") -> None:
    """
    Sends a beautifully styled multipart (Plain Text + HTML) OTP email via SMTP.
    """
    if not settings.SMTP_PASSWORD:
        raise RuntimeError("SMTP_PASSWORD is not configured in environment settings")

    msg = EmailMessage()
    clean_code = str(code).strip()

    if purpose == "login":
        subject = f"भू DRISTI — Verification Code [{clean_code}]"
    else:
        subject = f"भू DRISTI — Account Activation Code [{clean_code}]"

    msg["Subject"] = subject
    msg["From"] = f"भू DRISTI <{settings.SMTP_FROM_EMAIL}>"
    msg["To"] = email

    # 1. Plain text alternative (fallback)
    plain_text = render_otp_email_text(email, clean_code, purpose)
    msg.set_content(plain_text)

    # 2. Rich HTML alternative
    html_content = render_otp_email_html(email, clean_code, purpose)
    msg.add_alternative(html_content, subtype="html")

    logger.info("dispatching_styled_otp_email", extra={"email": email, "purpose": purpose})

    with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT, timeout=15) as server:
        server.starttls()
        server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
        refused = server.send_message(msg)
        if refused:
            raise smtplib.SMTPRecipientsRefused(refused)

    logger.info("styled_otp_email_dispatched_successfully", extra={"email": email})
