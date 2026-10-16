"""
Supabase Custom SMTP Email Templates for Bhu-Dristi.
These templates use Go template syntax ({{ .Token }}, {{ .ConfirmationURL }}, {{ .SiteURL }})
and can be pasted directly into Supabase Dashboard -> Authentication -> Email Templates,
or rendered locally for testing.
"""

def get_supabase_confirmation_template() -> str:
    return """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>भू DRISTI — Confirm Account Registration</title>
  <style>
    body, table, td, a { -webkit-text-size-adjust: 100%; -ms-text-size-adjust: 100%; }
    body { margin: 0; padding: 0; background-color: #0E1626; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; color: #1E293B; }
    @media only screen and (max-width: 620px) {
      .email-container { width: 100% !important; max-width: 100% !important; border-radius: 0 !important; }
      .mobile-padding { padding-left: 20px !important; padding-right: 20px !important; }
    }
  </style>
</head>
<body style="margin:0;padding:0;background-color:#0E1626;">
  <table width="100%" border="0" cellpadding="0" cellspacing="0" style="background:radial-gradient(circle at 50% 0%,#1A2844 0%,#0E1626 70%);padding:36px 10px;">
    <tr>
      <td align="center">
        <table class="email-container" width="600" border="0" cellpadding="0" cellspacing="0" style="width:600px;max-width:600px;background-color:#ffffff;border-radius:18px;overflow:hidden;box-shadow:0 16px 40px rgba(0,0,0,0.45);">
          <!-- Top Bar -->
          <tr>
            <td style="background-color:#070b14;padding:12px 26px;border-bottom:1px solid rgba(255,255,255,0.08)">
              <table width="100%" border="0" cellpadding="0" cellspacing="0">
                <tr>
                  <td align="left" style="font-family:'SF Mono',Consolas,monospace;font-size:11px;color:#94a3b8;letter-spacing:1.2px;text-transform:uppercase">
                    🛰️ NTRO · SIH 2026 · GEOSPATIAL INTELLIGENCE
                  </td>
                  <td align="right" style="font-family:'SF Mono',Consolas,monospace;font-size:11px;color:#10b981;letter-spacing:1px;font-weight:bold">
                    ● SECURE TRANSMISSION
                  </td>
                </tr>
              </table>
            </td>
          </tr>
          <!-- Hero Banner -->
          <tr>
            <td style="background:linear-gradient(135deg,#091326 0%,#152540 30%,#8c2e12 70%,#d6532b 90%);padding:36px 32px;color:#ffffff">
              <div style="display:inline-block;padding:5px 13px;background:rgba(255,255,255,0.16);border:1px solid rgba(255,255,255,0.28);border-radius:20px;font-size:10.5px;font-weight:700;letter-spacing:1.4px;text-transform:uppercase;margin-bottom:14px">
                ✨ NATIONAL GEOSPATIAL PLATFORM
              </div>
              <h1 style="margin:0 0 8px 0;font-size:26px;font-weight:800;letter-spacing:-0.5px;color:#ffffff">
                Confirm Your Account
              </h1>
              <p style="margin:0;font-size:14px;line-height:1.6;color:#cbd5e1;max-width:480px">
                Welcome to <strong>भू DRISTI</strong>. Activate your workspace credentials to access high-resolution AI Earth Observation pipelines.
              </p>
            </td>
          </tr>
          <!-- Body Content -->
          <tr>
            <td class="mobile-padding" style="padding:32px 32px 24px 32px;background-color:#ffffff">
              <div style="display:inline-block;padding:4px 12px;background-color:#e0f2fe;border:1px solid #bae6fd;border-radius:12px;font-family:'SF Mono',Consolas,monospace;font-size:10.5px;font-weight:700;color:#075985;letter-spacing:1.2px;text-transform:uppercase;margin-bottom:12px">
                ACCOUNT ACTIVATION · NEW USER
              </div>
              <p style="margin:0 0 20px 0;font-size:14px;line-height:1.65;color:#334155">
                Authorize your operator terminal by clicking the button below or entering your single-use activation code:
              </p>

              <!-- Token / OTP Display -->
              <table width="100%" border="0" cellpadding="0" cellspacing="0" style="background:#fff7ed;border:2px dashed #f97316;border-radius:14px;padding:22px 16px;text-align:center;margin:18px 0">
                <tr>
                  <td align="center">
                    <div style="font-family:'SF Mono',Consolas,monospace;font-size:11px;font-weight:700;letter-spacing:2px;text-transform:uppercase;color:#c2410c;margin-bottom:10px">
                      VERIFICATION PASSCODE
                    </div>
                    <div style="font-family:'SF Mono',Consolas,monospace;font-size:32px;font-weight:800;letter-spacing:8px;color:#d6532b">
                      {{ .Token }}
                    </div>
                    <div style="margin-top:14px">
                      <a href="{{ .ConfirmationURL }}" style="display:inline-block;background:linear-gradient(135deg,#d6532b 0%,#ea580c 100%);color:#ffffff;text-decoration:none;font-weight:700;font-size:13.5px;padding:12px 28px;border-radius:8px;box-shadow:0 4px 12px rgba(214,83,43,0.35)">
                        Confirm Account & Activate Workspace →
                      </a>
                    </div>
                  </td>
                </tr>
              </table>

              <!-- Notice -->
              <table width="100%" border="0" cellpadding="0" cellspacing="0" style="margin-top:16px;background-color:#f0fdf4;border-left:4px solid #10b981;border-radius:6px;padding:12px 16px">
                <tr>
                  <td valign="top" style="font-size:12px;color:#166534;line-height:1.6">
                    <strong>Zero-Trust Protocol:</strong> If you did not initiate this registration on भू DRISTI, no further action is required. This link will expire in 24 hours.
                  </td>
                </tr>
              </table>
            </td>
          </tr>
          <!-- Footer -->
          <tr>
            <td class="mobile-padding" style="background-color:#070b14;padding:24px 32px;text-align:center;color:#94a3b8;border-top:1px solid rgba(255,255,255,0.08)">
              <div style="font-size:13px;font-weight:700;color:#f1f5f9;margin-bottom:4px">
                भू DRISTI — National Geospatial Intelligence Platform
              </div>
              <div style="font-size:11px;color:#64748b">
                National Technical Research Organisation (NTRO) · Smart India Hackathon
              </div>
            </td>
          </tr>
        </table>
      </td>
    </tr>
  </table>
</body>
</html>"""


def get_supabase_recovery_template() -> str:
    return """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>भू DRISTI — Password Recovery Pass</title>
  <style>
    body, table, td, a { -webkit-text-size-adjust: 100%; -ms-text-size-adjust: 100%; }
    body { margin: 0; padding: 0; background-color: #0E1626; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; color: #1E293B; }
    @media only screen and (max-width: 620px) {
      .email-container { width: 100% !important; max-width: 100% !important; border-radius: 0 !important; }
      .mobile-padding { padding-left: 20px !important; padding-right: 20px !important; }
    }
  </style>
</head>
<body style="margin:0;padding:0;background-color:#0E1626;">
  <table width="100%" border="0" cellpadding="0" cellspacing="0" style="background:radial-gradient(circle at 50% 0%,#1A2844 0%,#0E1626 70%);padding:36px 10px;">
    <tr>
      <td align="center">
        <table class="email-container" width="600" border="0" cellpadding="0" cellspacing="0" style="width:600px;max-width:600px;background-color:#ffffff;border-radius:18px;overflow:hidden;box-shadow:0 16px 40px rgba(0,0,0,0.45);">
          <!-- Top Bar -->
          <tr>
            <td style="background-color:#070b14;padding:12px 26px;border-bottom:1px solid rgba(255,255,255,0.08)">
              <table width="100%" border="0" cellpadding="0" cellspacing="0">
                <tr>
                  <td align="left" style="font-family:'SF Mono',Consolas,monospace;font-size:11px;color:#94a3b8;letter-spacing:1.2px;text-transform:uppercase">
                    🛰️ NTRO · SIH 2026 · GEOSPATIAL INTELLIGENCE
                  </td>
                  <td align="right" style="font-family:'SF Mono',Consolas,monospace;font-size:11px;color:#ef4444;letter-spacing:1px;font-weight:bold">
                    ● RECOVERY PASS
                  </td>
                </tr>
              </table>
            </td>
          </tr>
          <!-- Hero Banner -->
          <tr>
            <td style="background:linear-gradient(135deg,#091326 0%,#152540 30%,#7f1d1d 70%,#b91c1c 90%);padding:36px 32px;color:#ffffff">
              <div style="display:inline-block;padding:5px 13px;background:rgba(255,255,255,0.16);border:1px solid rgba(255,255,255,0.28);border-radius:20px;font-size:10.5px;font-weight:700;letter-spacing:1.4px;text-transform:uppercase;margin-bottom:14px">
                🛡️ SECURITY & ACCESS RECOVERY
              </div>
              <h1 style="margin:0 0 8px 0;font-size:26px;font-weight:800;letter-spacing:-0.5px;color:#ffffff">
                Reset Your Password
              </h1>
              <p style="margin:0;font-size:14px;line-height:1.6;color:#fecaca;max-width:480px">
                A password reset sequence was initiated for your registered <strong>भू DRISTI</strong> operator account.
              </p>
            </td>
          </tr>
          <!-- Body Content -->
          <tr>
            <td class="mobile-padding" style="padding:32px 32px 24px 32px;background-color:#ffffff">
              <div style="display:inline-block;padding:4px 12px;background-color:#fef2f2;border:1px solid #fecaca;border-radius:12px;font-family:'SF Mono',Consolas,monospace;font-size:10.5px;font-weight:700;color:#991b1b;letter-spacing:1.2px;text-transform:uppercase;margin-bottom:12px">
                PASSWORD RECOVERY · VERIFICATION PASS
              </div>
              <p style="margin:0 0 20px 0;font-size:14px;line-height:1.65;color:#334155">
                Use the verification code below to authorize your password recovery, or click the direct recovery link:
              </p>

              <!-- Token Display -->
              <table width="100%" border="0" cellpadding="0" cellspacing="0" style="background:#fef2f2;border:2px dashed #ef4444;border-radius:14px;padding:22px 16px;text-align:center;margin:18px 0">
                <tr>
                  <td align="center">
                    <div style="font-family:'SF Mono',Consolas,monospace;font-size:11px;font-weight:700;letter-spacing:2px;text-transform:uppercase;color:#991b1b;margin-bottom:10px">
                      6-DIGIT RECOVERY TOKEN
                    </div>
                    <div style="font-family:'SF Mono',Consolas,monospace;font-size:32px;font-weight:800;letter-spacing:8px;color:#b91c1c">
                      {{ .Token }}
                    </div>
                    <div style="margin-top:14px">
                      <a href="{{ .ConfirmationURL }}" style="display:inline-block;background:linear-gradient(135deg,#b91c1c 0%,#dc2626 100%);color:#ffffff;text-decoration:none;font-weight:700;font-size:13.5px;padding:12px 28px;border-radius:8px;box-shadow:0 4px 12px rgba(185,28,28,0.35)">
                        Authorize Password Reset →
                      </a>
                    </div>
                  </td>
                </tr>
              </table>

              <table width="100%" border="0" cellpadding="0" cellspacing="0" style="margin-top:16px;background-color:#fffbeb;border-left:4px solid #f59e0b;border-radius:6px;padding:12px 16px">
                <tr>
                  <td valign="top" style="font-size:12px;color:#92400e;line-height:1.6">
                    <strong>Critical Notice:</strong> If you did not request this password recovery, someone may be attempting to access your workspace. Ignore this message and your existing password will remain secure.
                  </td>
                </tr>
              </table>
            </td>
          </tr>
          <!-- Footer -->
          <tr>
            <td class="mobile-padding" style="background-color:#070b14;padding:24px 32px;text-align:center;color:#94a3b8;border-top:1px solid rgba(255,255,255,0.08)">
              <div style="font-size:13px;font-weight:700;color:#f1f5f9;margin-bottom:4px">
                भू DRISTI — National Geospatial Intelligence Platform
              </div>
              <div style="font-size:11px;color:#64748b">
                National Technical Research Organisation (NTRO) · Smart India Hackathon
              </div>
            </td>
          </tr>
        </table>
      </td>
    </tr>
  </table>
</body>
</html>"""


def get_supabase_magic_link_template() -> str:
    return """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>भू DRISTI — Magic Link Sign-In</title>
  <style>
    body, table, td, a { -webkit-text-size-adjust: 100%; -ms-text-size-adjust: 100%; }
    body { margin: 0; padding: 0; background-color: #0E1626; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; color: #1E293B; }
    @media only screen and (max-width: 620px) {
      .email-container { width: 100% !important; max-width: 100% !important; border-radius: 0 !important; }
      .mobile-padding { padding-left: 20px !important; padding-right: 20px !important; }
    }
  </style>
</head>
<body style="margin:0;padding:0;background-color:#0E1626;">
  <table width="100%" border="0" cellpadding="0" cellspacing="0" style="background:radial-gradient(circle at 50% 0%,#1A2844 0%,#0E1626 70%);padding:36px 10px;">
    <tr>
      <td align="center">
        <table class="email-container" width="600" border="0" cellpadding="0" cellspacing="0" style="width:600px;max-width:600px;background-color:#ffffff;border-radius:18px;overflow:hidden;box-shadow:0 16px 40px rgba(0,0,0,0.45);">
          <!-- Top Bar -->
          <tr>
            <td style="background-color:#070b14;padding:12px 26px;border-bottom:1px solid rgba(255,255,255,0.08)">
              <table width="100%" border="0" cellpadding="0" cellspacing="0">
                <tr>
                  <td align="left" style="font-family:'SF Mono',Consolas,monospace;font-size:11px;color:#94a3b8;letter-spacing:1.2px;text-transform:uppercase">
                    🛰️ NTRO · SIH 2026 · GEOSPATIAL INTELLIGENCE
                  </td>
                  <td align="right" style="font-family:'SF Mono',Consolas,monospace;font-size:11px;color:#10b981;letter-spacing:1px;font-weight:bold">
                    ● FAST SIGN-IN
                  </td>
                </tr>
              </table>
            </td>
          </tr>
          <!-- Hero Banner -->
          <tr>
            <td style="background:linear-gradient(135deg,#091326 0%,#152540 30%,#0f766e 70%,#0d9488 90%);padding:36px 32px;color:#ffffff">
              <div style="display:inline-block;padding:5px 13px;background:rgba(255,255,255,0.16);border:1px solid rgba(255,255,255,0.28);border-radius:20px;font-size:10.5px;font-weight:700;letter-spacing:1.4px;text-transform:uppercase;margin-bottom:14px">
                ⚡ PASSWORDLESS ACCESS
              </div>
              <h1 style="margin:0 0 8px 0;font-size:26px;font-weight:800;letter-spacing:-0.5px;color:#ffffff">
                Sign In to भू DRISTI
              </h1>
              <p style="margin:0;font-size:14px;line-height:1.6;color:#ccfbf1;max-width:480px">
                Click the direct authorization link below to securely log into your geospatial intelligence workspace.
              </p>
            </td>
          </tr>
          <!-- Body Content -->
          <tr>
            <td class="mobile-padding" style="padding:32px 32px 24px 32px;background-color:#ffffff">
              <div style="display:inline-block;padding:4px 12px;background-color:#f0fdfa;border:1px solid #99f6e4;border-radius:12px;font-family:'SF Mono',Consolas,monospace;font-size:10.5px;font-weight:700;color:#0f766e;letter-spacing:1.2px;text-transform:uppercase;margin-bottom:12px">
                MAGIC LINK · OPERATOR TERMINAL ACCESS
              </div>
              <p style="margin:0 0 20px 0;font-size:14px;line-height:1.65;color:#334155">
                Authorize your session with a single click or enter the 6-digit code:
              </p>

              <!-- Button & Token -->
              <table width="100%" border="0" cellpadding="0" cellspacing="0" style="background:#f0fdfa;border:2px dashed #0d9488;border-radius:14px;padding:22px 16px;text-align:center;margin:18px 0">
                <tr>
                  <td align="center">
                    <div style="font-family:'SF Mono',Consolas,monospace;font-size:11px;font-weight:700;letter-spacing:2px;text-transform:uppercase;color:#0f766e;margin-bottom:10px">
                      SINGLE-USE LOGIN TOKEN
                    </div>
                    <div style="font-family:'SF Mono',Consolas,monospace;font-size:32px;font-weight:800;letter-spacing:8px;color:#0d9488">
                      {{ .Token }}
                    </div>
                    <div style="margin-top:14px">
                      <a href="{{ .ConfirmationURL }}" style="display:inline-block;background:linear-gradient(135deg,#0d9488 0%,#0f766e 100%);color:#ffffff;text-decoration:none;font-weight:700;font-size:13.5px;padding:12px 28px;border-radius:8px;box-shadow:0 4px 12px rgba(13,148,136,0.35)">
                        Instant Sign In to Workspace →
                      </a>
                    </div>
                  </td>
                </tr>
              </table>

              <table width="100%" border="0" cellpadding="0" cellspacing="0" style="margin-top:16px;background-color:#f8fafc;border-left:4px solid #64748b;border-radius:6px;padding:12px 16px">
                <tr>
                  <td valign="top" style="font-size:12px;color:#475569;line-height:1.6">
                    <strong>Notice:</strong> This magic link can only be used once and expires in 10 minutes. If you did not request this link, you can safely disregard it.
                  </td>
                </tr>
              </table>
            </td>
          </tr>
          <!-- Footer -->
          <tr>
            <td class="mobile-padding" style="background-color:#070b14;padding:24px 32px;text-align:center;color:#94a3b8;border-top:1px solid rgba(255,255,255,0.08)">
              <div style="font-size:13px;font-weight:700;color:#f1f5f9;margin-bottom:4px">
                भू DRISTI — National Geospatial Intelligence Platform
              </div>
              <div style="font-size:11px;color:#64748b">
                National Technical Research Organisation (NTRO) · Smart India Hackathon
              </div>
            </td>
          </tr>
        </table>
      </td>
    </tr>
  </table>
</body>
</html>"""


def get_supabase_invite_template() -> str:
    return """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>भू DRISTI — Workspace Invitation</title>
  <style>
    body, table, td, a { -webkit-text-size-adjust: 100%; -ms-text-size-adjust: 100%; }
    body { margin: 0; padding: 0; background-color: #0E1626; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; color: #1E293B; }
    @media only screen and (max-width: 620px) {
      .email-container { width: 100% !important; max-width: 100% !important; border-radius: 0 !important; }
      .mobile-padding { padding-left: 20px !important; padding-right: 20px !important; }
    }
  </style>
</head>
<body style="margin:0;padding:0;background-color:#0E1626;">
  <table width="100%" border="0" cellpadding="0" cellspacing="0" style="background:radial-gradient(circle at 50% 0%,#1A2844 0%,#0E1626 70%);padding:36px 10px;">
    <tr>
      <td align="center">
        <table class="email-container" width="600" border="0" cellpadding="0" cellspacing="0" style="width:600px;max-width:600px;background-color:#ffffff;border-radius:18px;overflow:hidden;box-shadow:0 16px 40px rgba(0,0,0,0.45);">
          <!-- Top Bar -->
          <tr>
            <td style="background-color:#070b14;padding:12px 26px;border-bottom:1px solid rgba(255,255,255,0.08)">
              <table width="100%" border="0" cellpadding="0" cellspacing="0">
                <tr>
                  <td align="left" style="font-family:'SF Mono',Consolas,monospace;font-size:11px;color:#94a3b8;letter-spacing:1.2px;text-transform:uppercase">
                    🛰️ NTRO · SIH 2026 · GEOSPATIAL INTELLIGENCE
                  </td>
                  <td align="right" style="font-family:'SF Mono',Consolas,monospace;font-size:11px;color:#6366f1;letter-spacing:1px;font-weight:bold">
                    ● INVITATION PASS
                  </td>
                </tr>
              </table>
            </td>
          </tr>
          <!-- Hero Banner -->
          <tr>
            <td style="background:linear-gradient(135deg,#091326 0%,#152540 30%,#4338ca 70%,#6366f1 90%);padding:36px 32px;color:#ffffff">
              <div style="display:inline-block;padding:5px 13px;background:rgba(255,255,255,0.16);border:1px solid rgba(255,255,255,0.28);border-radius:20px;font-size:10.5px;font-weight:700;letter-spacing:1.4px;text-transform:uppercase;margin-bottom:14px">
                👥 TEAM COLLABORATION
              </div>
              <h1 style="margin:0 0 8px 0;font-size:26px;font-weight:800;letter-spacing:-0.5px;color:#ffffff">
                You've Been Invited to भू DRISTI
              </h1>
              <p style="margin:0;font-size:14px;line-height:1.6;color:#e0e7ff;max-width:480px">
                You have been invited to join the National Geospatial Intelligence workspace to collaborate on Earth Observation missions.
              </p>
            </td>
          </tr>
          <!-- Body Content -->
          <tr>
            <td class="mobile-padding" style="padding:32px 32px 24px 32px;background-color:#ffffff">
              <div style="display:inline-block;padding:4px 12px;background-color:#eef2ff;border:1px solid #c7d2fe;border-radius:12px;font-family:'SF Mono',Consolas,monospace;font-size:10.5px;font-weight:700;color:#4338ca;letter-spacing:1.2px;text-transform:uppercase;margin-bottom:12px">
                OPERATOR ONBOARDING · WORKSPACE INVITATION
              </div>
              <p style="margin:0 0 20px 0;font-size:14px;line-height:1.65;color:#334155">
                Accept your invitation and configure your operator security profile:
              </p>

              <!-- Accept Button -->
              <div style="text-align:center;margin:24px 0">
                <a href="{{ .ConfirmationURL }}" style="display:inline-block;background:linear-gradient(135deg,#4f46e5 0%,#6366f1 100%);color:#ffffff;text-decoration:none;font-weight:700;font-size:14px;padding:14px 36px;border-radius:8px;box-shadow:0 4px 14px rgba(79,70,229,0.35)">
                  Accept Invitation & Join Workspace →
                </a>
              </div>
            </td>
          </tr>
          <!-- Footer -->
          <tr>
            <td class="mobile-padding" style="background-color:#070b14;padding:24px 32px;text-align:center;color:#94a3b8;border-top:1px solid rgba(255,255,255,0.08)">
              <div style="font-size:13px;font-weight:700;color:#f1f5f9;margin-bottom:4px">
                भू DRISTI — National Geospatial Intelligence Platform
              </div>
              <div style="font-size:11px;color:#64748b">
                National Technical Research Organisation (NTRO) · Smart India Hackathon
              </div>
            </td>
          </tr>
        </table>
      </td>
    </tr>
  </table>
</body>
</html>"""


def get_all_supabase_templates() -> dict:
    return {
        "confirmation": {
            "name": "Confirm Signup",
            "subject": "भू DRISTI — Confirm Account Registration",
            "html": get_supabase_confirmation_template(),
        },
        "recovery": {
            "name": "Reset Password",
            "subject": "भू DRISTI — Password Recovery Pass [{{ .Token }}]",
            "html": get_supabase_recovery_template(),
        },
        "magic_link": {
            "name": "Magic Link",
            "subject": "भू DRISTI — Magic Link Sign-In Pass [{{ .Token }}]",
            "html": get_supabase_magic_link_template(),
        },
        "invite": {
            "name": "Invite User",
            "subject": "भू DRISTI — Invitation to Join Geospatial Workspace",
            "html": get_supabase_invite_template(),
        },
    }
