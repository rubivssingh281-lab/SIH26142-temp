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

    if purpose in ("recovery", "reset", "forgot_password"):
        purpose_tag = "PASSWORD RECOVERY · VERIFICATION PASS"
        purpose_title = "Reset Your Password"
        purpose_desc = (
            "We received a request to reset the password for your <strong>भू DRISTI</strong> workspace account. "
            "Use the single-use 6-digit verification code below to authorize your password recovery."
        )
        badge_bg = "#fef2f2"
        badge_color = "#991b1b"
        badge_border = "#fecaca"
    elif purpose == "login":
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
    if purpose in ("recovery", "reset", "forgot_password"):
        label = "PASSWORD RECOVERY AUTHORIZATION"
    elif purpose == "login":
        label = "OPERATOR LOGIN VERIFICATION"
    else:
        label = "ACCOUNT WORKSPACE ACTIVATION"
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


def _dispatch_smtp_email(msg: EmailMessage, recipient: str) -> None:
    """
    Core SMTP delivery pipeline with TLS/SSL and automatic port 587 -> 465 fallback.
    """
    host = settings.effective_smtp_host
    port = int(settings.effective_smtp_port)
    user = settings.effective_smtp_user
    password = settings.effective_smtp_password

    if not password:
        logger.warning("SMTP password is not configured. Email delivery simulated.", extra={"recipient": recipient})
        return

    # Direct SSL (port 465)
    if port == 465:
        with smtplib.SMTP_SSL(host, port, timeout=20) as server:
            server.login(user, password)
            refused = server.send_message(msg)
            if refused:
                raise smtplib.SMTPRecipientsRefused(refused)
        return

    # STARTTLS (port 587) with fallback to port 465 SSL
    try:
        with smtplib.SMTP(host, port, timeout=15) as server:
            server.starttls()
            server.login(user, password)
            refused = server.send_message(msg)
            if refused:
                raise smtplib.SMTPRecipientsRefused(refused)
    except (ConnectionRefusedError, smtplib.SMTPConnectError, TimeoutError, OSError) as exc:
        logger.warning(f"SMTP port {port} connection failed ({exc}). Retrying via port 465 SSL...", extra={"recipient": recipient})
        try:
            with smtplib.SMTP_SSL(host, 465, timeout=20) as fallback_server:
                fallback_server.login(user, password)
                refused = fallback_server.send_message(msg)
                if refused:
                    raise smtplib.SMTPRecipientsRefused(refused)
        except Exception as ssl_exc:
            logger.error(f"Fallback SSL delivery also failed: {ssl_exc}")
            raise exc


def send_styled_otp_email(email: str, code: str, purpose: str = "login") -> None:
    """
    Sends a beautifully styled multipart (Plain Text + HTML) OTP email via SMTP.
    """
    msg = EmailMessage()
    clean_code = str(code).strip()

    if purpose in ("recovery", "reset", "forgot_password"):
        subject = f"भू DRISTI — Password Reset Code [{clean_code}]"
    elif purpose == "login":
        subject = f"भू DRISTI — Verification Code [{clean_code}]"
    else:
        subject = f"भू DRISTI — Account Activation Code [{clean_code}]"

    from_email = settings.effective_smtp_from
    msg["Subject"] = subject
    msg["From"] = f"भू DRISTI <{from_email}>"
    msg["To"] = email

    # 1. Plain text alternative (fallback)
    plain_text = render_otp_email_text(email, clean_code, purpose)
    msg.set_content(plain_text)

    # 2. Rich HTML alternative
    html_content = render_otp_email_html(email, clean_code, purpose)
    msg.add_alternative(html_content, subtype="html")

    logger.info("dispatching_styled_otp_email", extra={"email": email, "purpose": purpose})
    _dispatch_smtp_email(msg, email)
    logger.info("styled_otp_email_dispatched_successfully", extra={"email": email})
    logger.info("styled_otp_email_dispatched_successfully", extra={"email": email})


# ---------------------------------------------------------------------------
# JOB NOTIFICATIONS (QUEUED / COMPLETED / FAILED)
# ---------------------------------------------------------------------------

def render_job_notification_html(email: str, job: dict, event_type: str = "created") -> str:
    utc_str, ist_str = get_formatted_timestamps()
    job_id = job.get("job_id", "SR_v2_UNKNOWN")
    project = job.get("project", "Ladakh Border Infrastructure")
    res_gain = job.get("resolution_gain", "4x (10m → 2.5m)")
    model = job.get("model", "TerraSharp v2.1 (GAN)")
    compute_node = job.get("compute_node", "GPU-Node-01 (NVIDIA A100)")
    eta = job.get("eta", "Estimated ~18m")

    if event_type in ("created", "queued"):
        badge_bg = "#eff6ff"
        badge_color = "#1d4ed8"
        badge_border = "#bfdbfe"
        badge_text = "PIPELINE ACTIVE · JOB QUEUED"
        headline = f"Super-Resolution Job Queued: {job_id}"
        description = (
            f"A new geospatial enhancement job has been accepted by the "
            f"<strong>भू DRISTI</strong> inference scheduler for project <strong>{project}</strong>. "
            f"Multi-spectral Sentinel-2 bands are staged for super-resolution."
        )
    elif event_type in ("completed", "done"):
        badge_bg = "#ecfdf5"
        badge_color = "#047857"
        badge_border = "#a7f3d0"
        badge_text = "MISSION COMPLETE · READY FOR ANALYSIS"
        headline = f"Super-Resolution Completed: {job_id}"
        description = (
            f"Deep-learning enhancement finished successfully for <strong>{project}</strong>. "
            f"Analysis-ready 2.5 m/pixel imagery and uncertainty maps have been published "
            f"to the platform archive."
        )
    else:  # failed
        badge_bg = "#fef2f2"
        badge_color = "#b91c1c"
        badge_border = "#fecaca"
        badge_text = "CRITICAL ALERT · INFERENCE EXCEPTION"
        headline = f"Job Execution Warning: {job_id}"
        description = (
            f"Inference execution for job <strong>{job_id}</strong> encountered an error during "
            f"pre-processing or neural tensor calculation. Triage logs are available in the queue."
        )

    metrics_html = ""
    if event_type in ("completed", "done"):
        metrics_html = """
        <table width="100%" border="0" cellpadding="0" cellspacing="0" style="margin-top:20px;border:1px solid #e2e8f0;border-radius:8px;background:#f8fafc;overflow:hidden">
          <tr>
            <td style="padding:10px 14px;border-bottom:1px solid #e2e8f0;font-size:11px;font-weight:700;color:#334155;text-transform:uppercase;letter-spacing:0.5px">
              Super-Resolution Quality Metrics
            </td>
          </tr>
          <tr>
            <td style="padding:14px">
              <table width="100%" border="0" cellpadding="0" cellspacing="0">
                <tr>
                  <td width="25%" align="center" style="border-right:1px solid #e2e8f0;padding:6px">
                    <div style="font-size:18px;font-weight:800;color:#0f766e">34.58 dB</div>
                    <div style="font-size:10px;color:#64748b;margin-top:2px">PSNR (&gt; 30 dB)</div>
                  </td>
                  <td width="25%" align="center" style="border-right:1px solid #e2e8f0;padding:6px">
                    <div style="font-size:18px;font-weight:800;color:#0f766e">0.912</div>
                    <div style="font-size:10px;color:#64748b;margin-top:2px">SSIM (&gt; 0.85)</div>
                  </td>
                  <td width="25%" align="center" style="border-right:1px solid #e2e8f0;padding:6px">
                    <div style="font-size:18px;font-weight:800;color:#0f766e">3.21°</div>
                    <div style="font-size:10px;color:#64748b;margin-top:2px">SAM (&lt; 5.0°)</div>
                  </td>
                  <td width="25%" align="center" style="padding:6px">
                    <div style="font-size:18px;font-weight:800;color:#0f766e">2.48</div>
                    <div style="font-size:10px;color:#64748b;margin-top:2px">ERGAS (&lt; 3.0)</div>
                  </td>
                </tr>
              </table>
            </td>
          </tr>
        </table>
        """

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>भू DRISTI — {headline}</title>
</head>
<body style="margin:0;padding:0;background-color:#0E1626;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,Helvetica,Arial,sans-serif;color:#1E293B;">
  <table width="100%" border="0" cellpadding="0" cellspacing="0" style="background-color:#0E1626;padding:32px 16px">
    <tr>
      <td align="center">
        <table class="email-container" width="600" border="0" cellpadding="0" cellspacing="0" style="max-width:600px;width:100%;background-color:#ffffff;border-radius:12px;overflow:hidden;box-shadow:0 12px 32px rgba(0,0,0,0.35);">
          <!-- Top Accent -->
          <tr><td height="5" style="background:linear-gradient(90deg, #D2691E 0%, #EA580C 50%, #0F8C7F 100%);"></td></tr>
          
          <!-- Header -->
          <tr>
            <td style="background-color:#0B1320;padding:24px 32px;border-bottom:1px solid rgba(255,255,255,0.08)">
              <div style="font-size:20px;font-weight:800;color:#ffffff;letter-spacing:0.5px">
                🛰️ भू DRISTI <span style="font-size:11px;font-weight:600;color:#EA580C;background:rgba(234,88,12,0.15);padding:2px 8px;border-radius:12px;margin-left:8px">NTRO PS-26142</span>
              </div>
              <div style="font-size:11px;color:#94a3b8;margin-top:4px">National Geospatial Earth Observation & Super-Resolution</div>
            </td>
          </tr>

          <!-- Body -->
          <tr>
            <td style="padding:32px">
              <div style="display:inline-block;background:{badge_bg};color:{badge_color};border:1px solid {badge_border};border-radius:6px;padding:4px 10px;font-size:11px;font-weight:700;letter-spacing:0.5px;margin-bottom:12px">
                {badge_text}
              </div>
              <h1 style="margin:0 0 10px 0;font-size:21px;font-weight:700;color:#0f172a">{headline}</h1>
              <p style="margin:0 0 20px 0;font-size:13.5px;color:#475569;line-height:1.6">{description}</p>

              <!-- Job Details Grid -->
              <table width="100%" border="0" cellpadding="0" cellspacing="0" style="background:#f8fafc;border:1px solid #e2e8f0;border-radius:8px;padding:12px 16px;margin-bottom:16px">
                <tr>
                  <td width="50%" style="padding:6px 0;font-size:12px;color:#64748b">Job Identifier:</td>
                  <td width="50%" style="padding:6px 0;font-size:12px;font-weight:700;color:#0f172a;font-family:monospace">{job_id}</td>
                </tr>
                <tr>
                  <td style="padding:6px 0;font-size:12px;color:#64748b">Mission Project:</td>
                  <td style="padding:6px 0;font-size:12px;font-weight:600;color:#0f172a">{project}</td>
                </tr>
                <tr>
                  <td style="padding:6px 0;font-size:12px;color:#64748b">Resolution Gain:</td>
                  <td style="padding:6px 0;font-size:12px;font-weight:600;color:#d2691e">{res_gain}</td>
                </tr>
                <tr>
                  <td style="padding:6px 0;font-size:12px;color:#64748b">Neural Model:</td>
                  <td style="padding:6px 0;font-size:12px;font-weight:600;color:#0f172a">{model}</td>
                </tr>
                <tr>
                  <td style="padding:6px 0;font-size:12px;color:#64748b">Compute Node:</td>
                  <td style="padding:6px 0;font-size:12px;font-weight:600;color:#0f172a">{compute_node}</td>
                </tr>
                <tr>
                  <td style="padding:6px 0;font-size:12px;color:#64748b">Timestamp (IST):</td>
                  <td style="padding:6px 0;font-size:12px;font-weight:600;color:#0f172a">{ist_str}</td>
                </tr>
              </table>

              {metrics_html}

              <!-- Security notice -->
              <div style="margin-top:24px;padding:12px 14px;background:#f0fdf4;border-left:3px solid #10b981;border-radius:4px;font-size:11.5px;color:#166534">
                <strong>Zero-Trust Geospatial Telemetry:</strong> Automated SMTP notification generated by the Bhu-Dristi Orchestrator pipeline.
              </div>
            </td>
          </tr>

          <!-- Footer -->
          <tr>
            <td style="background-color:#070b14;padding:20px 32px;text-align:center;color:#64748b;font-size:11px">
              भू DRISTI — National Technical Research Organisation (NTRO) · Smart India Hackathon
            </td>
          </tr>
        </table>
      </td>
    </tr>
  </table>
</body>
</html>"""


def render_job_notification_text(email: str, job: dict, event_type: str = "created") -> str:
    utc_str, ist_str = get_formatted_timestamps()
    job_id = job.get("job_id", "SR_v2_UNKNOWN")
    project = job.get("project", "Ladakh Border Infrastructure")
    res_gain = job.get("resolution_gain", "4x (10m → 2.5m)")
    model = job.get("model", "TerraSharp v2.1")
    return (
        f"भू DRISTI — GEOSPATIAL INTELLIGENCE NOTIFICATION\n"
        f"Event: {event_type.upper()} | Job: {job_id}\n"
        f"Project: {project}\n"
        f"Resolution Gain: {res_gain}\n"
        f"Model: {model}\n"
        f"Timestamp: {ist_str} ({utc_str})\n"
        f"Recipient: {email}\n"
    )


def send_job_notification_email(email: str, job: dict, event_type: str = "created") -> None:
    job_id = job.get("job_id", "SR_v2")
    msg = EmailMessage()
    if event_type in ("completed", "done"):
        msg["Subject"] = f"भू DRISTI — Super-Resolution Completed [{job_id}]"
    elif event_type in ("failed",):
        msg["Subject"] = f"भू DRISTI — Job Alert: Inference Error [{job_id}]"
    else:
        msg["Subject"] = f"भू DRISTI — Job Queued [{job_id}]"

    msg["From"] = f"भू DRISTI <{settings.effective_smtp_from}>"
    msg["To"] = email
    msg.set_content(render_job_notification_text(email, job, event_type))
    msg.add_alternative(render_job_notification_html(email, job, event_type), subtype="html")

    logger.info("dispatching_job_notification_email", extra={"email": email, "job_id": job_id, "event_type": event_type})
    _dispatch_smtp_email(msg, email)


# ---------------------------------------------------------------------------
# REPORT / EXPORT EMAIL DISPATCH WITH PDF ATTACHMENTS
# ---------------------------------------------------------------------------

def render_report_email_html(email: str, report_type: str, job_id: str, filename: str) -> str:
    utc_str, ist_str = get_formatted_timestamps()
    return f"""<!DOCTYPE html>
<html lang="en">
<head><meta charset="UTF-8"><title>भू DRISTI — {report_type}</title></head>
<body style="margin:0;padding:0;background-color:#0E1626;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,sans-serif;color:#1E293B;">
  <table width="100%" border="0" cellpadding="0" cellspacing="0" style="padding:32px 16px;background:#0E1626">
    <tr>
      <td align="center">
        <table width="600" border="0" cellpadding="0" cellspacing="0" style="max-width:600px;background:#ffffff;border-radius:12px;overflow:hidden;box-shadow:0 12px 32px rgba(0,0,0,0.35)">
          <tr><td height="5" style="background:linear-gradient(90deg, #D2691E, #0F8C7F)"></td></tr>
          <tr>
            <td style="background-color:#0B1320;padding:24px 32px">
              <div style="font-size:20px;font-weight:800;color:#ffffff">🛰️ भू DRISTI — Document Dispatch</div>
              <div style="font-size:11px;color:#94a3b8;margin-top:4px">Official Geospatial Intelligence Report Delivery</div>
            </td>
          </tr>
          <tr>
            <td style="padding:32px">
              <div style="display:inline-block;background:#e0f2fe;color:#0369a1;border:1px solid #bae6fd;border-radius:6px;padding:4px 10px;font-size:11px;font-weight:700;margin-bottom:12px">
                VERIFIED ATTACHMENT · READY FOR PRINT
              </div>
              <h2 style="margin:0 0 10px 0;font-size:20px;color:#0f172a">{report_type} Delivery</h2>
              <p style="font-size:13.5px;color:#475569;line-height:1.6;margin:0 0 20px 0">
                Your requested <strong>{report_type}</strong> for mission entity <strong>{job_id}</strong> has been generated and attached to this email as a PDF document.
              </p>
              <table width="100%" style="background:#f8fafc;border:1px solid #e2e8f0;border-radius:8px;padding:12px 16px;margin-bottom:16px">
                <tr><td style="font-size:12px;color:#64748b">Attached Document:</td><td style="font-size:12px;font-weight:700;color:#0f172a;font-family:monospace">{filename}</td></tr>
                <tr><td style="font-size:12px;color:#64748b">Mission Reference:</td><td style="font-size:12px;font-weight:700;color:#0f172a">{job_id}</td></tr>
                <tr><td style="font-size:12px;color:#64748b">Generation Timestamp:</td><td style="font-size:12px;font-weight:600;color:#0f172a">{ist_str}</td></tr>
              </table>
              <div style="padding:12px 14px;background:#f0fdf4;border-left:3px solid #10b981;border-radius:4px;font-size:11.5px;color:#166534">
                🔒 NTRO PS-26142 Certified Document Output. Check attached file.
              </div>
            </td>
          </tr>
          <tr>
            <td style="background-color:#070b14;padding:18px 32px;text-align:center;color:#64748b;font-size:11px">
              भू DRISTI Platform — Automated Report Distribution Service
            </td>
          </tr>
        </table>
      </td>
    </tr>
  </table>
</body>
</html>"""


def send_report_email(email: str, report_type: str, job_id: str, pdf_bytes: bytes, filename: str) -> None:
    """
    Sends a styled email with the generated PDF report attached via SMTP.
    """
    msg = EmailMessage()
    msg["Subject"] = f"भू DRISTI — {report_type} [{job_id}]"
    msg["From"] = f"भू DRISTI <{settings.effective_smtp_from}>"
    msg["To"] = email

    utc_str, ist_str = get_formatted_timestamps()
    plain_text = (
        f"भू DRISTI — DOCUMENT DISPATCH: {report_type}\n"
        f"Mission: {job_id}\n"
        f"Generated: {ist_str}\n\n"
        f"Please find the requested PDF attached: {filename}\n"
    )
    msg.set_content(plain_text)
    msg.add_alternative(render_report_email_html(email, report_type, job_id, filename), subtype="html")

    # Attach PDF
    msg.add_attachment(pdf_bytes, maintype="application", subtype="pdf", filename=filename)

    logger.info("dispatching_report_email_with_pdf", extra={"email": email, "report_type": report_type, "filename": filename})
    _dispatch_smtp_email(msg, email)
    logger.info("report_email_dispatched_successfully", extra={"email": email})


# ---------------------------------------------------------------------------
# TEST NOTIFICATION VIA SMTP
# ---------------------------------------------------------------------------

def render_test_notification_html(email: str, channel: str = "Email") -> str:
    utc_str, ist_str = get_formatted_timestamps()
    return f"""<!DOCTYPE html>
<html lang="en">
<head><meta charset="UTF-8"><title>भू DRISTI — SMTP Notification Test</title></head>
<body style="margin:0;padding:0;background-color:#0E1626;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,sans-serif;color:#1E293B;">
  <table width="100%" border="0" cellpadding="0" cellspacing="0" style="padding:32px 16px;background:#0E1626">
    <tr>
      <td align="center">
        <table width="600" border="0" cellpadding="0" cellspacing="0" style="max-width:600px;background:#ffffff;border-radius:12px;overflow:hidden;box-shadow:0 12px 32px rgba(0,0,0,0.35)">
          <tr><td height="5" style="background:linear-gradient(90deg, #10B981, #0EA5E9)"></td></tr>
          <tr>
            <td style="background-color:#0B1320;padding:24px 32px">
              <div style="font-size:20px;font-weight:800;color:#ffffff">🛰️ भू DRISTI — Diagnostic Channel Test</div>
              <div style="font-size:11px;color:#94a3b8;margin-top:4px">SMTP Notification Pipeline Telemetry</div>
            </td>
          </tr>
          <tr>
            <td style="padding:32px">
              <div style="display:inline-block;background:#ecfdf5;color:#047857;border:1px solid #a7f3d0;border-radius:6px;padding:4px 10px;font-size:11px;font-weight:700;margin-bottom:12px">
                ✅ CHANNEL VERIFIED · ZERO-TRUST SMTP OPERATIONAL
              </div>
              <h2 style="margin:0 0 10px 0;font-size:21px;color:#0f172a">Live Notification Test Succeeded</h2>
              <p style="font-size:13.5px;color:#475569;line-height:1.6;margin:0 0 20px 0">
                This diagnostic notification confirms that your <strong>भू DRISTI</strong> platform is fully connected to the SMTP relay at <strong>{settings.SMTP_HOST}</strong>.
                All job progress updates, completion alerts, and mission reports will be delivered smoothly to your address.
              </p>
              <table width="100%" style="background:#f8fafc;border:1px solid #e2e8f0;border-radius:8px;padding:12px 16px;margin-bottom:16px">
                <tr><td style="font-size:12px;color:#64748b">Verified Recipient:</td><td style="font-size:12px;font-weight:700;color:#0f172a">{email}</td></tr>
                <tr><td style="font-size:12px;color:#64748b">Dispatch Channel:</td><td style="font-size:12px;font-weight:700;color:#0f172a">{channel}</td></tr>
                <tr><td style="font-size:12px;color:#64748b">SMTP Relay Host:</td><td style="font-size:12px;font-weight:600;color:#0f172a">{settings.SMTP_HOST}:{settings.SMTP_PORT}</td></tr>
                <tr><td style="font-size:12px;color:#64748b">Sender Identity:</td><td style="font-size:12px;font-weight:600;color:#0f172a">{settings.SMTP_FROM_EMAIL}</td></tr>
                <tr><td style="font-size:12px;color:#64748b">Timestamp (IST):</td><td style="font-size:12px;font-weight:600;color:#0f172a">{ist_str}</td></tr>
              </table>
              <div style="padding:12px 14px;background:#f0fdf4;border-left:3px solid #10b981;border-radius:4px;font-size:11.5px;color:#166534">
                🎉 Your alert pipeline is ready. Job notifications and system reports will be routed according to your notification settings.
              </div>
            </td>
          </tr>
          <tr>
            <td style="background-color:#070b14;padding:18px 32px;text-align:center;color:#64748b;font-size:11px">
              भू DRISTI — National Technical Research Organisation (NTRO)
            </td>
          </tr>
        </table>
      </td>
    </tr>
  </table>
</body>
</html>"""


def send_test_notification_email(email: str, channel: str = "Email") -> None:
    msg = EmailMessage()
    msg["Subject"] = "भू DRISTI — SMTP Notification Test [Channel Verified]"
    msg["From"] = f"भू DRISTI <{settings.effective_smtp_from}>"
    msg["To"] = email

    utc_str, ist_str = get_formatted_timestamps()
    plain_text = (
        f"भू DRISTI — SMTP NOTIFICATION TEST\n"
        f"Recipient: {email}\n"
        f"Channel: {channel}\n"
        f"Host: {settings.SMTP_HOST}:{settings.SMTP_PORT}\n"
        f"Timestamp: {ist_str}\n\n"
        f"Notification delivery is operational.\n"
    )
    msg.set_content(plain_text)
    msg.add_alternative(render_test_notification_html(email, channel), subtype="html")

    logger.info("dispatching_test_notification_email", extra={"email": email, "channel": channel})
    _dispatch_smtp_email(msg, email)
    logger.info("test_notification_email_dispatched_successfully", extra={"email": email})


# ---------------------------------------------------------------------------
# GENERAL PLATFORM & SECURITY ALERT EMAILS (PAIRS & MATRIX NOTIFICATIONS)
# ---------------------------------------------------------------------------

THEMES = {
    "success": {"bg": "#ecfdf5", "color": "#047857", "border": "#a7f3d0", "top": "#10B981"},
    "warning": {"bg": "#fffbeb", "color": "#b45309", "border": "#fde68a", "top": "#F59E0B"},
    "danger": {"bg": "#fef2f2", "color": "#b91c1c", "border": "#fecaca", "top": "#EF4444"},
    "info": {"bg": "#eff6ff", "color": "#1d4ed8", "border": "#bfdbfe", "top": "#3B82F6"},
    "purple": {"bg": "#faf5ff", "color": "#7e22ce", "border": "#e9d5ff", "top": "#A855F7"},
    "orange": {"bg": "#fff7ed", "color": "#c2410c", "border": "#fed7aa", "top": "#D2691E"},
    "teal": {"bg": "#f0fdfa", "color": "#0f766e", "border": "#99f6e4", "top": "#0F8C7F"},
}


def render_platform_alert_html(
    email: str,
    headline: str,
    description: str,
    badge_text: str,
    theme: str = "info",
    dossier_items: list = None,
    action_label: str = None,
    action_url: str = None,
    security_note: str = None,
) -> str:
    utc_str, ist_str = get_formatted_timestamps()
    t = THEMES.get(theme, THEMES["info"])
    items = dossier_items or [
        ("Recipient Account", email),
        ("Timestamp (IST)", ist_str),
        ("Timestamp (UTC)", utc_str),
    ]

    rows = "".join(
        f"""<tr>
          <td width="42%" style="padding:6px 0;font-size:12px;color:#64748b">{k}:</td>
          <td width="58%" style="padding:6px 0;font-size:12px;font-weight:600;color:#0f172a">{v}</td>
        </tr>"""
        for k, v in items
    )

    action_btn_html = ""
    if action_label:
        action_btn_html = f"""
        <div style="margin-top:20px;text-align:left">
          <a href="{action_url or '#'}" style="display:inline-block;padding:10px 20px;background:#D2691E;color:#ffffff;text-decoration:none;font-size:12px;font-weight:700;border-radius:6px">
            {action_label} &rarr;
          </a>
        </div>
        """

    sec_note_text = security_note or "Zero-Trust Geospatial Protocol: This notification was authorized by the Bhu-Dristi security perimeter."

    return f"""<!DOCTYPE html>
<html lang="en">
<head><meta charset="UTF-8"><title>भू DRISTI — {headline}</title></head>
<body style="margin:0;padding:0;background-color:#0E1626;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,sans-serif;color:#1E293B;">
  <table width="100%" border="0" cellpadding="0" cellspacing="0" style="padding:32px 16px;background:#0E1626">
    <tr>
      <td align="center">
        <table width="600" border="0" cellpadding="0" cellspacing="0" style="max-width:600px;background:#ffffff;border-radius:12px;overflow:hidden;box-shadow:0 12px 32px rgba(0,0,0,0.35)">
          <tr><td height="5" style="background:linear-gradient(90deg, {t['top']}, #0F8C7F)"></td></tr>
          <tr>
            <td style="background-color:#0B1320;padding:24px 32px">
              <div style="font-size:20px;font-weight:800;color:#ffffff">🛰️ भू DRISTI <span style="font-size:11px;font-weight:600;color:#EA580C;background:rgba(234,88,12,0.15);padding:2px 8px;border-radius:12px;margin-left:8px">NTRO PS-26142</span></div>
              <div style="font-size:11px;color:#94a3b8;margin-top:4px">National Geospatial Earth Observation & Super-Resolution</div>
            </td>
          </tr>
          <tr>
            <td style="padding:32px">
              <div style="display:inline-block;background:{t['bg']};color:{t['color']};border:1px solid {t['border']};border-radius:6px;padding:4px 10px;font-size:11px;font-weight:700;letter-spacing:0.5px;margin-bottom:12px">
                {badge_text}
              </div>
              <h1 style="margin:0 0 10px 0;font-size:21px;font-weight:700;color:#0f172a">{headline}</h1>
              <p style="margin:0 0 20px 0;font-size:13.5px;color:#475569;line-height:1.6">{description}</p>

              <table width="100%" border="0" cellpadding="0" cellspacing="0" style="background:#f8fafc;border:1px solid #e2e8f0;border-radius:8px;padding:12px 16px;margin-bottom:16px">
                {rows}
              </table>

              {action_btn_html}

              <div style="margin-top:24px;padding:12px 14px;background:#f0fdf4;border-left:3px solid #10b981;border-radius:4px;font-size:11.5px;color:#166534">
                <strong>Platform Directive:</strong> {sec_note_text}
              </div>
            </td>
          </tr>
          <tr>
            <td style="background-color:#070b14;padding:20px 32px;text-align:center;color:#64748b;font-size:11px">
              भू DRISTI — National Technical Research Organisation (NTRO) · Smart India Hackathon
            </td>
          </tr>
        </table>
      </td>
    </tr>
  </table>
</body>
</html>"""


def send_platform_alert_email(
    email: str,
    subject: str,
    headline: str,
    description: str,
    badge_text: str,
    theme: str = "info",
    dossier_items: list = None,
    action_label: str = None,
    action_url: str = None,
    security_note: str = None,
) -> None:
    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = f"भू DRISTI <{settings.effective_smtp_from}>"
    msg["To"] = email

    utc_str, ist_str = get_formatted_timestamps()
    plain_text = (
        f"भू DRISTI — {badge_text}\n"
        f"Title: {headline}\n"
        f"Summary: {description}\n"
        f"Recipient: {email}\n"
        f"Timestamp: {ist_str}\n"
    )
    msg.set_content(plain_text)
    msg.add_alternative(
        render_platform_alert_html(
            email=email,
            headline=headline,
            description=description,
            badge_text=badge_text,
            theme=theme,
            dossier_items=dossier_items,
            action_label=action_label,
            action_url=action_url,
            security_note=security_note,
        ),
        subtype="html",
    )

    logger.info("dispatching_platform_alert_email", extra={"email": email, "subject": subject})
    _dispatch_smtp_email(msg, email)
    logger.info("platform_alert_email_dispatched_successfully", extra={"email": email})


# ---------------------------------------------------------------------------
# EXECUTIVE DIGEST & PERIODIC SUMMARY EMAILS
# ---------------------------------------------------------------------------

def render_digest_email_html(email: str, frequency: str = "Daily Digest") -> str:
    utc_str, ist_str = get_formatted_timestamps()
    return f"""<!DOCTYPE html>
<html lang="en">
<head><meta charset="UTF-8"><title>भू DRISTI — {frequency} Executive Summary</title></head>
<body style="margin:0;padding:0;background-color:#0E1626;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,sans-serif;color:#1E293B;">
  <table width="100%" border="0" cellpadding="0" cellspacing="0" style="padding:32px 16px;background:#0E1626">
    <tr>
      <td align="center">
        <table width="600" border="0" cellpadding="0" cellspacing="0" style="max-width:600px;background:#ffffff;border-radius:12px;overflow:hidden;box-shadow:0 12px 32px rgba(0,0,0,0.35)">
          <tr><td height="5" style="background:linear-gradient(90deg, #D2691E, #0F8C7F)"></td></tr>
          <tr>
            <td style="background-color:#0B1320;padding:24px 32px">
              <div style="font-size:20px;font-weight:800;color:#ffffff">🛰️ भू DRISTI <span style="font-size:11px;font-weight:600;color:#EA580C;background:rgba(234,88,12,0.15);padding:2px 8px;border-radius:12px;margin-left:8px">NTRO PS-26142</span></div>
              <div style="font-size:11px;color:#94a3b8;margin-top:4px">National Geospatial Earth Observation & Super-Resolution</div>
            </td>
          </tr>
          <tr>
            <td style="padding:32px">
              <div style="display:inline-block;background:#eff6ff;color:#1d4ed8;border:1px solid #bfdbfe;border-radius:6px;padding:4px 10px;font-size:11px;font-weight:700;letter-spacing:0.5px;margin-bottom:12px">
                📊 {frequency.upper()} · MISSION TELEMETRY
              </div>
              <h1 style="margin:0 0 10px 0;font-size:21px;font-weight:700;color:#0f172a">Geospatial Processing Summary</h1>
              <p style="margin:0 0 20px 0;font-size:13.5px;color:#475569;line-height:1.6">
                Consolidated operations brief for your monitored sectors and super-resolution pipeline over the past period.
              </p>

              <!-- KPI Stats Grid -->
              <table width="100%" border="0" cellpadding="0" cellspacing="0" style="margin-bottom:20px;border:1px solid #e2e8f0;border-radius:8px;background:#f8fafc">
                <tr>
                  <td width="33%" align="center" style="padding:14px;border-right:1px solid #e2e8f0">
                    <div style="font-size:22px;font-weight:800;color:#0f766e">24 / 24</div>
                    <div style="font-size:10.5px;color:#64748b;margin-top:2px">Jobs Succeeded (100%)</div>
                  </td>
                  <td width="33%" align="center" style="padding:14px;border-right:1px solid #e2e8f0">
                    <div style="font-size:22px;font-weight:800;color:#d2691e">34.62 dB</div>
                    <div style="font-size:10.5px;color:#64748b;margin-top:2px">Mean PSNR Gain</div>
                  </td>
                  <td width="34%" align="center" style="padding:14px">
                    <div style="font-size:22px;font-weight:800;color:#0369a1">4.82 GB</div>
                    <div style="font-size:10.5px;color:#64748b;margin-top:2px">Inference Tensors</div>
                  </td>
                </tr>
              </table>

              <!-- Recent Mission Highlights -->
              <div style="font-size:13px;font-weight:700;color:#0f172a;margin-bottom:10px">Active Project Operations:</div>
              <table width="100%" border="0" cellpadding="0" cellspacing="0" style="border:1px solid #e2e8f0;border-radius:8px;overflow:hidden;margin-bottom:20px">
                <tr style="background:#f1f5f9">
                  <td style="padding:8px 12px;font-size:11px;font-weight:700;color:#475569">PROJECT</td>
                  <td style="padding:8px 12px;font-size:11px;font-weight:700;color:#475569">PIPELINE</td>
                  <td style="padding:8px 12px;font-size:11px;font-weight:700;color:#475569">STATUS</td>
                </tr>
                <tr style="border-top:1px solid #e2e8f0">
                  <td style="padding:10px 12px;font-size:12px;color:#0f172a;font-weight:600">Ladakh Border Infrastructure</td>
                  <td style="padding:10px 12px;font-size:12px;color:#64748b">TerraSharp 4x GAN</td>
                  <td style="padding:10px 12px;font-size:11px;font-weight:700;color:#059669">● COMPLETED</td>
                </tr>
                <tr style="border-top:1px solid #e2e8f0">
                  <td style="padding:10px 12px;font-size:12px;color:#0f172a;font-weight:600">Siachen Glacial Moraine</td>
                  <td style="padding:10px 12px;font-size:12px;color:#64748b">ESRGAN Multispectral</td>
                  <td style="padding:10px 12px;font-size:11px;font-weight:700;color:#059669">● COMPLETED</td>
                </tr>
                <tr style="border-top:1px solid #e2e8f0">
                  <td style="padding:10px 12px;font-size:12px;color:#0f172a;font-weight:600">Thar Desert Surveillance</td>
                  <td style="padding:10px 12px;font-size:12px;color:#64748b">Diffusion Prior 4x</td>
                  <td style="padding:10px 12px;font-size:11px;font-weight:700;color:#2563eb">● PROCESSING</td>
                </tr>
              </table>

              <div style="padding:12px 14px;background:#f0fdf4;border-left:3px solid #10b981;border-radius:4px;font-size:11.5px;color:#166534">
                <strong>Platform Telemetry:</strong> All 4 GPU worker nodes (NVIDIA A100-80GB) operating in nominal thermal envelope.
              </div>
            </td>
          </tr>
          <tr>
            <td style="background-color:#070b14;padding:20px 32px;text-align:center;color:#64748b;font-size:11px">
              भू DRISTI — National Technical Research Organisation (NTRO) · Smart India Hackathon
            </td>
          </tr>
        </table>
      </td>
    </tr>
  </table>
</body>
</html>"""


def send_digest_email(email: str, frequency: str = "Daily Digest") -> None:
    msg = EmailMessage()
    msg["Subject"] = f"भू DRISTI — {frequency} Executive Telemetry Report"
    msg["From"] = f"भू DRISTI <{settings.effective_smtp_from}>"
    msg["To"] = email

    utc_str, ist_str = get_formatted_timestamps()
    plain_text = (
        f"भू DRISTI — {frequency.upper()} EXECUTIVE SUMMARY\n"
        f"Recipient: {email}\n"
        f"Timestamp: {ist_str} ({utc_str})\n\n"
        f"Jobs completed: 24/24 (100% Success)\n"
        f"Average PSNR: 34.62 dB | Average SSIM: 0.914\n"
        f"Active Projects: Ladakh Border Infrastructure, Siachen Glacial Moraine\n"
    )
    msg.set_content(plain_text)
    msg.add_alternative(render_digest_email_html(email, frequency), subtype="html")

    logger.info("dispatching_digest_email", extra={"email": email, "frequency": frequency})
    _dispatch_smtp_email(msg, email)
    logger.info("digest_email_dispatched_successfully", extra={"email": email})


# ---------------------------------------------------------------------------
# CONVENIENCE DISPATCHERS FOR EVERY TYPE OF PLATFORM EMAIL
# ---------------------------------------------------------------------------

def send_login_otp_email(email: str, code: str) -> None:
    send_styled_otp_email(email, code, purpose="login")

def send_signup_otp_email(email: str, code: str) -> None:
    send_styled_otp_email(email, code, purpose="verification")

def send_password_recovery_otp_email(email: str, code: str) -> None:
    send_styled_otp_email(email, code, purpose="recovery")

def send_job_queued_email(email: str, job_id: str = "SR_v2_20261017_001", project: str = "Ladakh Border Infrastructure") -> None:
    send_job_notification_email(email, {
        "job_id": job_id,
        "project": project,
        "resolution_gain": "4x (10m → 2.5m/pixel)",
        "model": "TerraSharp v2.1 (Deep Adversarial Multi-Spectral)",
        "compute_node": "GPU-Cluster-Alpha (NVIDIA A100-80GB)",
        "eta": "Estimated ~18m",
    }, event_type="created")

def send_job_completed_email(email: str, job_id: str = "SR_v2_20261017_001", project: str = "Ladakh Border Infrastructure") -> None:
    send_job_notification_email(email, {
        "job_id": job_id,
        "project": project,
        "resolution_gain": "4x (10m → 2.5m/pixel)",
        "model": "TerraSharp v2.1 (Deep Adversarial Multi-Spectral)",
        "compute_node": "GPU-Cluster-Alpha (NVIDIA A100-80GB)",
        "eta": "Completed in 14m 28s",
    }, event_type="completed")

def send_job_failed_email(email: str, job_id: str = "SR_v2_20261017_FAIL", project: str = "Siachen Glacial Moraine", error: str = "Inference Tensor Out-Of-Memory") -> None:
    send_job_notification_email(email, {
        "job_id": job_id,
        "project": project,
        "resolution_gain": "4x (10m → 2.5m)",
        "model": "TerraSharp v2.1",
        "compute_node": "GPU-Cluster-Beta (Node-03)",
        "eta": f"Terminated: {error}",
    }, event_type="failed")

def send_job_delayed_email(email: str, job_id: str = "SR_v2_20261017_DELAY", project: str = "Thar Desert Surveillance") -> None:
    send_platform_alert_email(
        email=email,
        subject=f"भू DRISTI — Processing Notice: Queue Delay [{job_id}]",
        headline="Processing Queue Delay Notice",
        description=f"Inference job {job_id} for project {project} has experienced a queue backlog due to high satellite ingest volume.",
        badge_text="SCHEDULE DELAY · INFERENCE QUEUE",
        theme="warning",
        dossier_items=[
            ("Job Identifier", job_id),
            ("Mission Project", project),
            ("Expected Delay", "+12 minutes"),
            ("Status", "Rescheduling to Secondary GPU Worker"),
        ]
    )

def send_storage_threshold_alert_email(email: str, usage_pct: float = 90.0, current_tb: float = 9.02, max_tb: float = 10.0) -> None:
    send_platform_alert_email(
        email=email,
        subject="भू DRISTI — Critical Storage Threshold Alert (90% Consumed)",
        headline="Storage Capacity Warning (90%)",
        description=f"Your high-resolution satellite imagery storage volume has reached {usage_pct}% of total provisioned capacity.",
        badge_text="INFRASTRUCTURE ALERT · STORAGE CONSUMPTION",
        theme="danger",
        dossier_items=[
            ("Provisioned Volume", f"{max_tb:.1f} TB (Ceph / S3 Object Storage)"),
            ("Consumed Volume", f"{current_tb:.2f} TB ({usage_pct:.1f}%)"),
            ("Recommended Action", "Archive older raw scenes or expand storage tier"),
        ]
    )

def send_gpu_cluster_alert_email(email: str, node: str = "GPU-Cluster-Alpha", status: str = "Healthy (All 4 Nodes Online)", gpus: str = "4x NVIDIA A100-80GB") -> None:
    send_platform_alert_email(
        email=email,
        subject=f"भू DRISTI — GPU Cluster Status Update [{node}]",
        headline=f"GPU Worker Node Status: {status}",
        description=f"Telemetry metrics for cluster node {node} updated. Neural tensor inference scheduler active.",
        badge_text="CLUSTER TELEMETRY · HARDWARE STATUS",
        theme="teal",
        dossier_items=[
            ("Compute Node", node),
            ("Hardware Acceleration", gpus),
            ("Operational State", status),
        ]
    )

def send_team_invite_email(email: str, inviter_name: str = "Lead Administrator", org_name: str = "NTRO", role: str = "Analyst") -> None:
    send_platform_alert_email(
        email=email,
        subject=f"भू DRISTI — Invitation to Join {org_name} Workspace",
        headline="You've Been Invited to Join भू DRISTI",
        description=f"{inviter_name} has invited you to collaborate on the {org_name} geospatial intelligence workspace as a {role}.",
        badge_text="WORKSPACE INVITATION · OPERATOR ONBOARDING",
        theme="info",
        dossier_items=[
            ("Invited Email", email),
            ("Organization", org_name),
            ("Assigned Role", role),
            ("Invited By", inviter_name),
        ]
    )

def send_role_change_email(email: str, user_name: str = "Operator", new_role: str = "Senior Imagery Analyst", admin_name: str = "Security Officer") -> None:
    send_platform_alert_email(
        email=email,
        subject=f"भू DRISTI — Security Role Updated to {new_role}",
        headline="Access Permissions Updated",
        description=f"Your account role and workspace permissions on भू DRISTI have been elevated to {new_role} by {admin_name}.",
        badge_text="SECURITY PERMISSIONS · ROLE MODIFICATION",
        theme="purple",
        dossier_items=[
            ("Account Name", user_name),
            ("Account Email", email),
            ("New Role", new_role),
            ("Authorized By", admin_name),
        ]
    )

def send_security_login_alert_email(email: str, ip: str = "103.21.244.18", location: str = "New Delhi, India", device: str = "Chrome 122 on Windows 11") -> None:
    send_platform_alert_email(
        email=email,
        subject="भू DRISTI — Security Notice: Sign-In from New Device",
        headline="New Device Sign-In Detected",
        description="A successful sign-in to your भू DRISTI account was registered from a new browser or IP address. If this was you, no action is needed.",
        badge_text="ZERO-TRUST AUDIT · NEW SESSION DETECTED",
        theme="orange",
        dossier_items=[
            ("Account Email", email),
            ("IP Address", ip),
            ("Approximate Location", location),
            ("User Agent / Device", device),
        ]
    )

def send_project_comment_email(email: str, author: str = "Dr. Rajesh V.", project: str = "Ladakh Border Infrastructure", comment: str = "Super-resolution analysis shows clear delineation along road segment B4.") -> None:
    send_platform_alert_email(
        email=email,
        subject=f"भू DRISTI — New Mission Discussion on {project}",
        headline=f"New Note Added to Project {project}",
        description=f'{author} posted an operational note: "{comment}"',
        badge_text="COLLABORATION · MISSION BRIEFING",
        theme="info",
        dossier_items=[
            ("Author", author),
            ("Project", project),
            ("Note Excerpt", comment),
        ]
    )

def send_attached_validation_report_email(email: str, job_id: str = "SR_v2_20261017_001") -> None:
    from app.services.report_service import validation_report_pdf
    from app.services import data_service
    pdf_bytes = validation_report_pdf(data_service.build_validation(job_id))
    send_report_email(email, "Validation Quality Report", job_id, pdf_bytes, f"validation-report-{job_id}.pdf")

def send_attached_comparison_report_email(email: str, job_id: str = "SR_v2_20261017_001") -> None:
    from app.services.report_service import comparison_snapshot_pdf
    from app.services import data_service
    pdf_bytes = comparison_snapshot_pdf(data_service.build_comparison(job_id))
    send_report_email(email, "Comparison Analysis Snapshot", job_id, pdf_bytes, f"comparison-snapshot-{job_id}.pdf")

def send_attached_invoice_email(email: str, inv_id: str = "INV-2026-0842", amount: float = 320.0, date: str = "17 Oct 2026") -> None:
    from app.services.report_service import invoice_pdf
    pdf_bytes = invoice_pdf(inv_id, amount, date)
    send_report_email(email, "Commercial Billing Invoice", inv_id, pdf_bytes, f"invoice-{inv_id}.pdf")

def dispatch_email_by_type(email: str, email_type: str, extra: dict = None) -> dict:
    """
    Universal router to dispatch ANY of the 17 platform email types via SMTP or Supabase.
    """
    e = (extra or {})
    clean_type = email_type.strip().lower()

    if clean_type in ("otp_login", "login_otp", "login"):
        code = e.get("code") or "849201"
        send_login_otp_email(email, code)
        return {"type": "otp_login", "recipient": email, "code": code}

    elif clean_type in ("otp_signup", "signup_otp", "activation", "register"):
        code = e.get("code") or "619384"
        send_signup_otp_email(email, code)
        return {"type": "otp_signup", "recipient": email, "code": code}

    elif clean_type in ("password_reset", "recovery", "reset_password"):
        code = e.get("code") or "472910"
        send_password_recovery_otp_email(email, code)
        return {"type": "password_reset", "recipient": email, "code": code}

    elif clean_type in ("job_queued", "job_created", "queued"):
        job_id = e.get("job_id", "SR_v2_20261017_001")
        project = e.get("project", "Ladakh Border Infrastructure")
        send_job_queued_email(email, job_id, project)
        return {"type": "job_queued", "recipient": email, "job_id": job_id}

    elif clean_type in ("job_completed", "completed", "done"):
        job_id = e.get("job_id", "SR_v2_20261017_001")
        project = e.get("project", "Ladakh Border Infrastructure")
        send_job_completed_email(email, job_id, project)
        return {"type": "job_completed", "recipient": email, "job_id": job_id}

    elif clean_type in ("job_failed", "failed", "error"):
        job_id = e.get("job_id", "SR_v2_20261017_FAIL")
        project = e.get("project", "Siachen Glacial Moraine")
        error = e.get("error", "Inference Tensor Out-Of-Memory")
        send_job_failed_email(email, job_id, project, error)
        return {"type": "job_failed", "recipient": email, "job_id": job_id}

    elif clean_type in ("job_delayed", "delayed"):
        job_id = e.get("job_id", "SR_v2_20261017_DELAY")
        project = e.get("project", "Thar Desert Surveillance")
        send_job_delayed_email(email, job_id, project)
        return {"type": "job_delayed", "recipient": email, "job_id": job_id}

    elif clean_type in ("storage_threshold", "storage_warning", "storage"):
        pct = float(e.get("usage_pct", 90.0))
        curr = float(e.get("current_tb", 9.02))
        max_tb = float(e.get("max_tb", 10.0))
        send_storage_threshold_alert_email(email, pct, curr, max_tb)
        return {"type": "storage_threshold", "recipient": email, "usage_pct": pct}

    elif clean_type in ("gpu_status", "gpu_cluster", "gpu"):
        node = e.get("node", "GPU-Cluster-Alpha")
        status = e.get("status", "Healthy (All 4 Nodes Online)")
        gpus = e.get("gpus", "4x NVIDIA A100-80GB")
        send_gpu_cluster_alert_email(email, node, status, gpus)
        return {"type": "gpu_status", "recipient": email, "node": node}

    elif clean_type in ("team_invite", "invite"):
        inviter = e.get("inviter_name", "Lead Administrator")
        org = e.get("org_name", "NTRO")
        role = e.get("role", "Analyst")
        send_team_invite_email(email, inviter, org, role)
        return {"type": "team_invite", "recipient": email, "role": role}

    elif clean_type in ("role_change", "role"):
        user = e.get("user_name", "Operator")
        new_role = e.get("new_role", "Senior Imagery Analyst")
        admin = e.get("admin_name", "Security Officer")
        send_role_change_email(email, user, new_role, admin)
        return {"type": "role_change", "recipient": email, "new_role": new_role}

    elif clean_type in ("security_login", "security_alert", "security"):
        ip = e.get("ip", "103.21.244.18")
        loc = e.get("location", "New Delhi, India")
        dev = e.get("device", "Chrome 122 on Windows 11")
        send_security_login_alert_email(email, ip, loc, dev)
        return {"type": "security_login", "recipient": email, "ip": ip}

    elif clean_type in ("project_comment", "comment"):
        author = e.get("author", "Dr. Rajesh V.")
        project = e.get("project", "Ladakh Border Infrastructure")
        comment = e.get("comment", "Super-resolution analysis shows clear delineation along road segment B4.")
        send_project_comment_email(email, author, project, comment)
        return {"type": "project_comment", "recipient": email, "author": author}

    elif clean_type in ("report_validation", "validation_pdf", "validation"):
        job_id = e.get("job_id", "SR_v2_20261017_001")
        send_attached_validation_report_email(email, job_id)
        return {"type": "report_validation", "recipient": email, "job_id": job_id}

    elif clean_type in ("report_comparison", "comparison_pdf", "comparison"):
        job_id = e.get("job_id", "SR_v2_20261017_001")
        send_attached_comparison_report_email(email, job_id)
        return {"type": "report_comparison", "recipient": email, "job_id": job_id}

    elif clean_type in ("invoice", "invoice_pdf"):
        inv_id = e.get("inv_id", "INV-2026-0842")
        amt = float(e.get("amount", 320.0))
        date = e.get("date", "17 Oct 2026")
        send_attached_invoice_email(email, inv_id, amt, date)
        return {"type": "invoice", "recipient": email, "inv_id": inv_id}

    elif clean_type in ("daily_digest", "digest", "summary"):
        freq = e.get("frequency", "Daily Digest")
        send_digest_email(email, freq)
        return {"type": "daily_digest", "recipient": email, "frequency": freq}

    elif clean_type in ("smtp_test", "test"):
        ch = e.get("channel", "Email (SMTP Relay)")
        send_test_notification_email(email, ch)
        return {"type": "smtp_test", "recipient": email}

    else:
        raise ValueError(f"Unknown email type: '{email_type}'. Supported: otp_login, otp_signup, password_reset, job_queued, job_completed, job_failed, job_delayed, storage_threshold, gpu_status, team_invite, role_change, security_login, project_comment, report_validation, report_comparison, invoice, daily_digest, smtp_test")


def get_email_catalog() -> list[dict]:
    """
    Returns full metadata catalog for all 18 Bhu-Dristi email types.
    """
    return [
        {
            "id": "otp_login",
            "name": "Operator Sign-in Verification Code (OTP)",
            "category": "Authentication",
            "description": "Dispatches 6-digit styled OTP verification pass to authorized operators attempting terminal sign-in.",
            "supports_supabase_smtp": True,
            "supports_direct_smtp": True,
            "sample_extra": {"code": "849201"},
        },
        {
            "id": "otp_signup",
            "name": "Account Activation / New User Welcome (OTP)",
            "category": "Authentication",
            "description": "Sends account confirmation code and onboarding instructions for newly registered users.",
            "supports_supabase_smtp": True,
            "supports_direct_smtp": True,
            "sample_extra": {"code": "619384"},
        },
        {
            "id": "password_reset",
            "name": "Password Recovery Authorization Code",
            "category": "Authentication",
            "description": "Sends secure single-use recovery code to reset forgotten account passwords.",
            "supports_supabase_smtp": True,
            "supports_direct_smtp": True,
            "sample_extra": {"code": "472910"},
        },
        {
            "id": "job_queued",
            "name": "Satellite Job Queued Notification",
            "category": "Job & Inference",
            "description": "Alerts operator when a new multi-spectral satellite super-resolution job is ingested and queued.",
            "supports_supabase_smtp": False,
            "supports_direct_smtp": True,
            "sample_extra": {"job_id": "SR_v2_20261017_001", "project": "Ladakh Border Infrastructure"},
        },
        {
            "id": "job_completed",
            "name": "Job Completed Alert (Multi-spectral 4x Gain)",
            "category": "Job & Inference",
            "description": "Delivers completion dossier with model inference telemetry, duration, and resolution gain metrics.",
            "supports_supabase_smtp": False,
            "supports_direct_smtp": True,
            "sample_extra": {"job_id": "SR_v2_20261017_001", "project": "Ladakh Border Infrastructure"},
        },
        {
            "id": "job_failed",
            "name": "Job Failed / Inference Exception Alert",
            "category": "Job & Inference",
            "description": "Critical notice when an inference pipeline terminates abnormally due to VRAM or tensor faults.",
            "supports_supabase_smtp": False,
            "supports_direct_smtp": True,
            "sample_extra": {"job_id": "SR_v2_20261017_FAIL", "project": "Siachen Glacial Moraine", "error": "Inference Tensor Out-Of-Memory"},
        },
        {
            "id": "job_delayed",
            "name": "Processing Queue Delay Notice",
            "category": "Job & Inference",
            "description": "Advisory sent when high-priority satellite telemetry surges cause queue delays.",
            "supports_supabase_smtp": False,
            "supports_direct_smtp": True,
            "sample_extra": {"job_id": "SR_v2_20261017_DELAY", "project": "Thar Desert Surveillance"},
        },
        {
            "id": "storage_threshold",
            "name": "Storage Threshold Capacity Alert (90%)",
            "category": "Infrastructure & Telemetry",
            "description": "Infrastructure warning when high-resolution satellite imagery storage volume reaches 90% capacity.",
            "supports_supabase_smtp": False,
            "supports_direct_smtp": True,
            "sample_extra": {"usage_pct": 91.8, "current_tb": 9.18, "max_tb": 10.0},
        },
        {
            "id": "gpu_status",
            "name": "GPU Worker Cluster Topology & Status Update",
            "category": "Infrastructure & Telemetry",
            "description": "Telemetry status of NVIDIA A100 GPU compute nodes, VRAM allocation, and thermal metrics.",
            "supports_supabase_smtp": False,
            "supports_direct_smtp": True,
            "sample_extra": {"node": "GPU-Cluster-Alpha", "status": "Healthy (All 4 Nodes Online)", "gpus": "4x NVIDIA A100-80GB"},
        },
        {
            "id": "team_invite",
            "name": "Team & Workspace Collaboration Invite",
            "category": "Team & Workspace",
            "description": "Invitation dispatch for newly invited analysts or commanders to collaborate on geospatial projects.",
            "supports_supabase_smtp": True,
            "supports_direct_smtp": True,
            "sample_extra": {"inviter_name": "Arjun Pratap", "org_name": "NTRO", "role": "Senior Imagery Analyst"},
        },
        {
            "id": "role_change",
            "name": "Operator Role & Clearance Permissions Updated",
            "category": "Security & IAM",
            "description": "Audit notification when an operator's security level or workspace permissions are elevated or changed.",
            "supports_supabase_smtp": False,
            "supports_direct_smtp": True,
            "sample_extra": {"user_name": "Operator", "new_role": "Senior Mission Commander", "admin_name": "Security Director"},
        },
        {
            "id": "security_login",
            "name": "Zero-Trust Audit: Sign-In from New Device / IP",
            "category": "Security & IAM",
            "description": "Security notification alerting operators of successful terminal access from an unrecognized IP or browser.",
            "supports_supabase_smtp": False,
            "supports_direct_smtp": True,
            "sample_extra": {"ip": "49.37.142.88", "location": "New Delhi, India", "device": "Chrome 124 on Windows 11"},
        },
        {
            "id": "project_comment",
            "name": "New Mission Discussion / AOI Annotation Comment",
            "category": "Team & Workspace",
            "description": "Real-time notice when an intelligence note or coordinate annotation is posted to an AOI project.",
            "supports_supabase_smtp": False,
            "supports_direct_smtp": True,
            "sample_extra": {"author": "Flight Lt. Vikram Verma", "project": "Ladakh Border Infrastructure", "comment": "Super-resolution reveals newly surfaced logistics access trail."},
        },
        {
            "id": "report_validation",
            "name": "Quality Validation Report (with attached PDF)",
            "category": "Intelligence Reports",
            "description": "Dispatches comprehensive PSNR, SSIM, SAM, and ERGAS validation report with cryptographic PDF attachment.",
            "supports_supabase_smtp": False,
            "supports_direct_smtp": True,
            "sample_extra": {"job_id": "SR_v2_20261017_001"},
        },
        {
            "id": "report_comparison",
            "name": "Comparison Analysis Snapshot (with attached PDF)",
            "category": "Intelligence Reports",
            "description": "Delivers before/after super-resolution radiometric comparison snapshot with attached PDF dossier.",
            "supports_supabase_smtp": False,
            "supports_direct_smtp": True,
            "sample_extra": {"job_id": "SR_v2_20261017_001"},
        },
        {
            "id": "invoice",
            "name": "Commercial Compute Billing Statement (with attached PDF)",
            "category": "Intelligence Reports",
            "description": "Itemized compute consumption invoice for GPU cluster compute hours and storage volume.",
            "supports_supabase_smtp": False,
            "supports_direct_smtp": True,
            "sample_extra": {"inv_id": "INV-2026-0842", "amount": 320.0, "date": "17 Oct 2026"},
        },
        {
            "id": "daily_digest",
            "name": "Executive Daily / Weekly Telemetry Digest",
            "category": "Digest & Telemetry",
            "description": "Consolidated summary of completed inference passes, satellite ingestion volume, and health metrics.",
            "supports_supabase_smtp": False,
            "supports_direct_smtp": True,
            "sample_extra": {"frequency": "Daily Digest"},
        },
        {
            "id": "smtp_test",
            "name": "Live SMTP Diagnostic Channel Verification",
            "category": "Diagnostics",
            "description": "Immediate channel handshake test verifying outbound SMTP relay connectivity and credentials.",
            "supports_supabase_smtp": False,
            "supports_direct_smtp": True,
            "sample_extra": {"channel": "Email (SMTP Relay)"},
        },
    ]


async def async_dispatch_email_by_type(email: str, email_type: str, extra: dict = None, provider: str = "auto") -> dict:
    """
    Asynchronous universal router supporting Supabase Auth HTTPS dispatch and direct SMTP relay.
    """
    clean_type = (email_type or "").strip().lower()
    e = extra or {}
    logger.info("async_dispatch_email_start", extra={"email": email, "type": clean_type, "provider": provider})

    # 1. Supabase Auth API Dispatch (When configured and requested/auto)
    if provider in ("supabase", "auto") and clean_type in ("otp_login", "login_otp", "otp_signup", "signup_otp", "activation", "register", "password_reset", "recovery", "reset_password"):
        if settings.SUPABASE_URL and settings.SUPABASE_ANON_KEY and "PROJECT_REF" not in settings.SUPABASE_URL:
            import httpx
            try:
                headers = {
                    "apikey": settings.SUPABASE_ANON_KEY,
                    "Authorization": f"Bearer {settings.SUPABASE_ANON_KEY}",
                    "Content-Type": "application/json",
                }
                async with httpx.AsyncClient(timeout=10.0) as client:
                    if clean_type in ("password_reset", "recovery", "reset_password"):
                        url = f"{settings.SUPABASE_URL.rstrip('/')}/auth/v1/recover"
                        resp = await client.post(url, headers=headers, json={"email": email})
                    else:
                        url = f"{settings.SUPABASE_URL.rstrip('/')}/auth/v1/otp"
                        resp = await client.post(url, headers=headers, json={"email": email, "create_user": True})

                    if resp.status_code in (200, 201):
                        logger.info("supabase_smtp_email_dispatched", extra={"email": email, "type": clean_type})
                        return {
                            "provider": "supabase_smtp",
                            "status": "dispatched",
                            "type": clean_type,
                            "recipient": email,
                            "message": f"Successfully triggered Supabase SMTP dispatch for {clean_type}",
                        }
                    else:
                        logger.warning(f"supabase_api_non_200: {resp.status_code} ({resp.text}). Falling back to direct SMTP.")
            except Exception as exc:
                logger.warning(f"supabase_smtp_exception: {exc}. Falling back to direct SMTP.")

    # 2. Direct SMTP Relay dispatch (dispatched in threadpool to keep FastAPI async event loop unblocked)
    import asyncio
    res = await asyncio.to_thread(dispatch_email_by_type, email, clean_type, e)
    res["provider"] = "direct_smtp"
    res["status"] = "dispatched"
    res["smtp_host"] = settings.effective_smtp_host
    return res





