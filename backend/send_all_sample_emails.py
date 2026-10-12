"""
Dispatch script to send all types and pairs of Bhu-Dristi emails to hehehegoteee@gmail.com
Includes:
- Channel Diagnostic / Test SMTP Email
- All 6 Job & Processing Alerts (Job Completed, Job Failed, Processing Delayed, Validation Report Ready with PDF, Storage Threshold 90%, GPU Status Change)
- All 4 Team & Account Alerts (Team Member Invited, Role Changed, Project Comment, Security Login from New Device)
- Daily Digest Summary
- Operator Login Verification OTP (6 styled digit boxes)
- Account Activation OTP (6 styled digit boxes)
- Comparison Snapshot Report (with attached PDF)
- Commercial Compute Invoice (with attached PDF)
"""
import sys
import os
import time
import datetime
from zoneinfo import ZoneInfo

# Ensure UTF-8 output on Windows
sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.core.config import settings
from app.services.email_service import (
    send_test_notification_email,
    send_job_notification_email,
    send_platform_alert_email,
    send_report_email,
    send_styled_otp_email,
    send_digest_email,
    get_formatted_timestamps,
)
from app.services.report_service import (
    validation_report_pdf,
    comparison_snapshot_pdf,
    invoice_pdf,
)

TARGET_RECIPIENT = "hehehegoteee@gmail.com"

print(f"======================================================================")
print(f"🛰️  भू DRISTI — COMPLETE EMAIL DISPATCH ROSTER")
print(f"Recipient Target: {TARGET_RECIPIENT}")
print(f"SMTP Relay:       {settings.SMTP_HOST}:{settings.SMTP_PORT}")
print(f"Sender:           {settings.SMTP_FROM_EMAIL}")
print(f"======================================================================\n")

utc_str, ist_str = get_formatted_timestamps()

dispatches = [
    # -------------------------------------------------------------
    # 1. CHANNEL DIAGNOSTIC / TEST SMTP EMAIL
    # -------------------------------------------------------------
    {
        "index": 1,
        "name": "SMTP Diagnostic Test Email",
        "category": "Notification Channel Test",
        "func": lambda: send_test_notification_email(
            email=TARGET_RECIPIENT,
            channel="Email (SMTP Relay)",
        ),
    },

    # -------------------------------------------------------------
    # 2. JOB COMPLETED (Job & Processing Alerts - Row 1)
    # -------------------------------------------------------------
    {
        "index": 2,
        "name": "Job Completed Alert (Multi-spectral 4x Gain)",
        "category": "Job & Processing Alerts",
        "func": lambda: send_job_notification_email(
            email=TARGET_RECIPIENT,
            job={
                "job_id": "SR_v2_20240521",
                "project": "Ladakh Border Infrastructure",
                "resolution_gain": "4x (10m → 2.5m/pixel)",
                "model": "TerraSharp v2.1 (Deep Adversarial Multi-Spectral)",
                "compute_node": "GPU-Cluster-Alpha (NVIDIA A100-80GB)",
                "eta": "Completed in 14m 28s",
            },
            event_type="completed",
        ),
    },

    # -------------------------------------------------------------
    # 3. JOB FAILED (Job & Processing Alerts - Row 2)
    # -------------------------------------------------------------
    {
        "index": 3,
        "name": "Job Failed Alert (Inference Tensor Exception)",
        "category": "Job & Processing Alerts",
        "func": lambda: send_job_notification_email(
            email=TARGET_RECIPIENT,
            job={
                "job_id": "SR_v2_20240528_FAIL",
                "project": "Siachen Glacial Moraine",
                "resolution_gain": "4x (10m → 2.5m)",
                "model": "TerraSharp v2.1",
                "compute_node": "GPU-Cluster-Beta (Node-03)",
                "eta": "Terminated at 42% execution",
            },
            event_type="failed",
        ),
    },

    # -------------------------------------------------------------
    # 4. PROCESSING DELAYED (Job & Processing Alerts - Row 3)
    # -------------------------------------------------------------
    {
        "index": 4,
        "name": "Processing Delayed Alert",
        "category": "Job & Processing Alerts",
        "func": lambda: send_platform_alert_email(
            email=TARGET_RECIPIENT,
            subject="भू DRISTI — Pipeline Notice: Processing Delayed [SR_v2_20240522]",
            headline="Processing Queue Delayed: SR_v2_20240522",
            description=(
                "Super-resolution job <strong>SR_v2_20240522</strong> for project "
                "<strong>Ladakh Border Infrastructure</strong> experienced a scheduler pause "
                "due to GPU memory re-allocation and higher-priority NTRO emergency task preemption. "
                "Inference will automatically resume at priority rank 2."
            ),
            badge_text="QUEUE ADVISORY · PROCESSING DELAYED",
            theme="warning",
            dossier_items=[
                ("Job Reference", "SR_v2_20240522"),
                ("Monitored AOI", "Ladakh Sector 4B (34.14° N, 77.57° E)"),
                ("Original ETA", "11:15 AM IST"),
                ("Adjusted ETA", "11:32 AM IST (+17 mins)"),
                ("Current Queue Rank", "Rank 02 of 18"),
                ("Scheduler Node", "Cluster-Primary-Orchestrator"),
            ],
            action_label="Open Live Queue Monitor",
            action_url="http://localhost:3000/queue",
            security_note="Zero-Trust Scheduler Protocol: GPU preemption logged in immutable audit trail.",
        ),
    },

    # -------------------------------------------------------------
    # 5. VALIDATION REPORT READY (Job & Processing Alerts - Row 4 with PDF!)
    # -------------------------------------------------------------
    {
        "index": 5,
        "name": "Validation Report Ready (with attached PDF)",
        "category": "Job & Processing Alerts",
        "func": lambda: (
            lambda pdf_bytes: send_report_email(
                email=TARGET_RECIPIENT,
                report_type="Quality Validation Report",
                job_id="SR_v2_20240521",
                pdf_bytes=pdf_bytes,
                filename="Validation_Report_SR_v2_20240521.pdf",
            )
        )(
            validation_report_pdf({
                "job_id": "SR_v2_20240521",
                "compare_against": "WorldView-3 (0.3m High-Resolution Reference)",
                "metrics": [
                    {"label": "PSNR", "value": "34.58", "unit": " dB", "delta": "2.4", "delta_dir": "up", "rating": "Excellent"},
                    {"label": "SSIM", "value": "0.912", "unit": "", "delta": "0.08", "delta_dir": "up", "rating": "Optimal"},
                    {"label": "SAM", "value": "3.21", "unit": "°", "delta": "0.4", "delta_dir": "down", "rating": "Low error"},
                    {"label": "ERGAS", "value": "2.48", "unit": "", "delta": "0.3", "delta_dir": "down", "rating": "Nominal"},
                ],
                "correlation": {"r": 0.94},
                "tasks": [
                    {"task": "Runway Boundary Segmentation", "metric": "mIoU", "result": 0.88, "status": "pass", "reference": ">= 0.80"},
                    {"task": "Vehicle Detection (0.5m)", "metric": "mAP@50", "result": 0.81, "status": "pass", "reference": ">= 0.75"},
                    {"task": "Road Network Extraction", "metric": "F1-Score", "result": 0.92, "status": "pass", "reference": ">= 0.85"},
                ],
            })
        ),
    },

    # -------------------------------------------------------------
    # 6. STORAGE THRESHOLD REACHED (90%) (Job & Processing Alerts - Row 5)
    # -------------------------------------------------------------
    {
        "index": 6,
        "name": "Storage Threshold Reached (90%) Alert",
        "category": "Job & Processing Alerts",
        "func": lambda: send_platform_alert_email(
            email=TARGET_RECIPIENT,
            subject="भू DRISTI — Critical Storage Warning: 90% Capacity Reached",
            headline="Geospatial Storage Threshold Reached (91.8%)",
            description=(
                "Your primary high-speed NVMe satellite imagery storage volume has exceeded "
                "the warning watermark at <strong>9.18 TB of 10.00 TB</strong>. "
                "Automated lifecycle archival to AWS S3 Glacier will trigger if capacity reaches 95%."
            ),
            badge_text="CAPACITY WARNING · 90% THRESHOLD REACHED",
            theme="danger",
            dossier_items=[
                ("Current Consumed Space", "9.18 TB (91.8%)"),
                ("Total Volume Capacity", "10.00 TB Enterprise NVMe"),
                ("Archived Super-Resolution Jobs", "148 Missions"),
                ("Fastest Growing Project", "Ladakh Border Infrastructure (3.4 TB)"),
                ("Cold Storage Policy", "Auto-tier older than 60 days to AWS Glacier"),
            ],
            action_label="Manage Storage & Archive Settings",
            action_url="http://localhost:3000/settings",
            security_note="Platform Governance: Hot storage exhaustion will pause newly queued large ingestion batches.",
        ),
    },

    # -------------------------------------------------------------
    # 7. GPU CLUSTER STATUS CHANGE (Job & Processing Alerts - Row 6)
    # -------------------------------------------------------------
    {
        "index": 7,
        "name": "GPU Cluster Status Change Alert",
        "category": "Job & Processing Alerts",
        "func": lambda: send_platform_alert_email(
            email=TARGET_RECIPIENT,
            subject="भू DRISTI — Cluster Alert: GPU Worker Topology Updated",
            headline="Inference Cluster Topology Rebalanced",
            description=(
                "GPU Orchestrator has re-allocated worker nodes to absorb surge demand for "
                "multi-spectral satellite upscaling. 4x NVIDIA A100-80GB accelerators have been assigned "
                "to the primary inference cluster with NCCL peer-to-peer tensor parallelism."
            ),
            badge_text="CLUSTER TOPOLOGY UPDATE · GPU STATUS CHANGE",
            theme="purple",
            dossier_items=[
                ("Active Compute Nodes", "4x NVIDIA A100 SXM4 (80GB VRAM each)"),
                ("Current Aggregate VRAM", "320 GB HBM2e Memory"),
                ("Cluster State", "ONLINE · BALANCED · 88.4% UTILIZATION"),
                ("Thermals & Power", "61°C avg · 310W / 400W TDP"),
                ("Active Task Pool", "Ladakh Batch 4x (Bands B02, B03, B04, B08)"),
            ],
            action_label="View Cluster Hardware Metrics",
            action_url="http://localhost:3000/queue",
            security_note="Infrastructure Directive: Hardware telemetry monitored continuously via NVIDIA DCGM.",
        ),
    },

    # -------------------------------------------------------------
    # 8. NEW TEAM MEMBER INVITED (Team & Account Alerts - Row 1)
    # -------------------------------------------------------------
    {
        "index": 8,
        "name": "New Team Member Invited Alert",
        "category": "Team & Account Alerts",
        "func": lambda: send_platform_alert_email(
            email=TARGET_RECIPIENT,
            subject="भू DRISTI — Team Update: New Member Invited",
            headline="New Operator Invited to Bhu-Dristi Workspace",
            description=(
                "A new analyst invitation has been dispatched for <strong>Dr. Rajesh Sundaram</strong> "
                "(Senior Geospatial Specialist, NTRO) by workspace administrator <strong>Arjun Pratap</strong>. "
                "The invitee has been assigned read/execute roles on Project Ladakh Border Infrastructure."
            ),
            badge_text="WORKSPACE COLLABORATION · TEAM INVITE",
            theme="info",
            dossier_items=[
                ("Invited Member", "Dr. Rajesh Sundaram (r.sundaram@ntro.gov.in)"),
                ("Invited By", "Arjun Pratap (NTRO Lead Analyst)"),
                ("Assigned Role", "Geospatial Analyst (Level 2)"),
                ("Workspace Scope", "Restricted Earth Observation Projects"),
                ("Invitation Expiry", "7 days (19 Oct 2026)"),
            ],
            action_label="Review Team & Access Permissions",
            action_url="http://localhost:3000/settings",
            security_note="Zero-Trust IAM: Invitations require government MFA activation before imagery access.",
        ),
    },

    # -------------------------------------------------------------
    # 9. ROLE / PERMISSION CHANGED (Team & Account Alerts - Row 2)
    # -------------------------------------------------------------
    {
        "index": 9,
        "name": "Role / Permission Changed Alert",
        "category": "Team & Account Alerts",
        "func": lambda: send_platform_alert_email(
            email=TARGET_RECIPIENT,
            subject="भू DRISTI — Security Notice: Operator Role & Permissions Changed",
            headline="Operator Role & Security Clearance Updated",
            description=(
                "The role and security permissions for operator account <strong>hehehegoteee@gmail.com</strong> "
                "were modified by the NTRO Platform Security Officer. "
                "Clearance elevated from <em>Geospatial Analyst</em> to <em>Senior Mission Commander</em>."
            ),
            badge_text="SECURITY & IAM · PERMISSION PRIVILEGE ESCALATION",
            theme="orange",
            dossier_items=[
                ("Operator Account", TARGET_RECIPIENT),
                ("Previous Privilege", "Geospatial Analyst (Level 2)"),
                ("New Assigned Role", "Senior Mission Commander (Level 3)"),
                ("Grant Details", "Full Super-Resolution Queue Control & Model Tuning"),
                ("Authorizing Officer", "Security Director, NTRO Operations Command"),
            ],
            action_label="View Updated Account Permissions",
            action_url="http://localhost:3000/settings",
            security_note="Audit Log: Security role change cryptographically signed under policy NTRO-IAM-4401.",
        ),
    },

    # -------------------------------------------------------------
    # 10. NEW COMMENT ON PROJECT (Team & Account Alerts - Row 3)
    # -------------------------------------------------------------
    {
        "index": 10,
        "name": "New Comment on Project Alert",
        "category": "Team & Account Alerts",
        "func": lambda: send_platform_alert_email(
            email=TARGET_RECIPIENT,
            subject="भू DRISTI — Project Collaboration: New Comment on Ladakh Infrastructure",
            headline="New Intelligence Comment on AOI Sector 4B",
            description=(
                "Analyst <strong>Flight Lt. Vikram Verma</strong> posted a strategic observation "
                "on tile <strong>#482-619 (Sector 4B North Ridge)</strong> in project "
                "<strong>Ladakh Border Infrastructure</strong>:"
                "<blockquote style='margin:12px 0;padding:10px 14px;background:#f8fafc;border-left:3px solid #0f766e;font-style:italic;color:#334155'>"
                "“4x Super-resolution reveals newly surfaced unpaved logistics access trail along coordinates "
                "34°08'42\"N, 77°34'18\"E. Spectral reflectance indicates recent soil compaction. Validation confirmed.”"
                "</blockquote>"
            ),
            badge_text="PROJECT COLLABORATION · AOI ANNOTATION",
            theme="teal",
            dossier_items=[
                ("Project Name", "Ladakh Border Infrastructure"),
                ("Comment Author", "Flight Lt. Vikram Verma (Imagery Analyst)"),
                ("Tagged Region", "Sector 4B North Ridge (Tile #482-619)"),
                ("Attached Artifact", "SR_v2_20240521 2.5m GeoTIFF Layer"),
            ],
            action_label="Inspect Annotated AOI in Viewer",
            action_url="http://localhost:3000/comparison",
            security_note="Operational Security: Comments in classified workspaces are restricted to cleared personnel.",
        ),
    },

    # -------------------------------------------------------------
    # 11. SECURITY LOGIN FROM NEW DEVICE (Team & Account Alerts - Row 4)
    # -------------------------------------------------------------
    {
        "index": 11,
        "name": "Security Login from New Device Alert",
        "category": "Team & Account Alerts",
        "func": lambda: send_platform_alert_email(
            email=TARGET_RECIPIENT,
            subject="भू DRISTI — Security Alert: Login Detected from New Device",
            headline="Zero-Trust Audit: Sign-In From Unrecognized Terminal",
            description=(
                "A successful operator authentication sequence was established from a previously "
                "unrecognized browser and hardware fingerprint. If this was you, no action is necessary. "
                "If you did not authorize this login, revoke active terminal sessions immediately."
            ),
            badge_text="ZERO-TRUST AUDIT · NEW DEVICE AUTHENTICATED",
            theme="danger",
            dossier_items=[
                ("Operator Identity", TARGET_RECIPIENT),
                ("IP Address", "49.37.142.88 (New Delhi, India · National NIC Gateway)"),
                ("Browser / OS", "Google Chrome 124.0.6367 / Windows 11 Enterprise"),
                ("Auth Mechanism", "Multi-Factor Styled OTP + HMAC Session Token"),
                ("Session Token", "sess_sec_994a8e27c1f03"),
            ],
            action_label="Revoke Terminal & Lock Account",
            action_url="http://localhost:3000/settings",
            security_note="Zero-Trust Directive: An unrecognized device requires explicit confirmation within 24 hours.",
        ),
    },

    # -------------------------------------------------------------
    # 12. DAILY DIGEST SUMMARY (From Notification Frequency)
    # -------------------------------------------------------------
    {
        "index": 12,
        "name": "Daily Digest Executive Telemetry Summary",
        "category": "Notification Frequency & Digest",
        "func": lambda: send_digest_email(
            email=TARGET_RECIPIENT,
            frequency="Daily Digest",
        ),
    },

    # -------------------------------------------------------------
    # 13. OPERATOR SIGN-IN OTP (Styled Digit Boxes)
    # -------------------------------------------------------------
    {
        "index": 13,
        "name": "Operator Sign-in Verification Code (OTP)",
        "category": "Platform Authentication & Security",
        "func": lambda: send_styled_otp_email(
            email=TARGET_RECIPIENT,
            code="849201",
            purpose="login",
        ),
    },

    # -------------------------------------------------------------
    # 14. ACCOUNT ACTIVATION / WELCOME OTP
    # -------------------------------------------------------------
    {
        "index": 14,
        "name": "Account Activation / Welcome Code (OTP)",
        "category": "Platform Authentication & Security",
        "func": lambda: send_styled_otp_email(
            email=TARGET_RECIPIENT,
            code="592734",
            purpose="activation",
        ),
    },

    # -------------------------------------------------------------
    # 15. COMPARISON SNAPSHOT REPORT (with attached PDF)
    # -------------------------------------------------------------
    {
        "index": 15,
        "name": "Comparison Snapshot Report (with attached PDF)",
        "category": "Intelligence Reporting & PDF Exports",
        "func": lambda: (
            lambda pdf_bytes: send_report_email(
                email=TARGET_RECIPIENT,
                report_type="Comparison Snapshot",
                job_id="SR_v2_20240520_1030",
                pdf_bytes=pdf_bytes,
                filename="Comparison_Snapshot_SR_v2_20240520_1030.pdf",
            )
        )(
            comparison_snapshot_pdf({
                "job_id": "SR_v2_20240520_1030",
                "coordinate": "34°08'42\"N, 77°34'18\"E",
                "lr_image": "Ladakh_B02_B04_10m",
                "sr_image": "Ladakh_SR_2.5m",
                "lr_resolution": "Sentinel-2 · 10m Ground Sample Distance",
                "sr_resolution": "TerraSharp · 2.5m Enhanced (4x Super-Resolution)",
                "metrics": [
                    {"label": "PSNR", "value": "34.58 dB", "threshold": "> 30 dB", "pass": True},
                    {"label": "SSIM", "value": "0.912", "threshold": "> 0.85", "pass": True},
                    {"label": "SAM", "value": "3.21 deg", "threshold": "< 5.0 deg", "pass": True},
                ],
                "pixel": {
                    "coordinate": "34.1450° N, 77.5717° E (Pixel X: 482, Y: 619)",
                    "bands": [
                        {"band": "B02 Blue (490 nm)", "reflectance": 0.142},
                        {"band": "B03 Green (560 nm)", "reflectance": 0.218},
                        {"band": "B04 Red (665 nm)", "reflectance": 0.195},
                        {"band": "B08 NIR (842 nm)", "reflectance": 0.485},
                    ],
                },
            })
        ),
    },

    # -------------------------------------------------------------
    # 16. COMMERCIAL COMPUTE BILLING INVOICE (with attached PDF)
    # -------------------------------------------------------------
    {
        "index": 16,
        "name": "Commercial Compute Billing Invoice (with attached PDF)",
        "category": "Intelligence Reporting & PDF Exports",
        "func": lambda: (
            lambda pdf_bytes: send_report_email(
                email=TARGET_RECIPIENT,
                report_type="Commercial Compute Invoice",
                job_id="INV-2026-0042",
                pdf_bytes=pdf_bytes,
                filename="Invoice_INV-2026-0042.pdf",
            )
        )(
            invoice_pdf(
                inv_id="INV-2026-0042",
                amount=84500.0,
                date_str="12 Oct 2026",
            )
        ),
    },
]

total = len(dispatches)
success_count = 0
failed_count = 0

for item in dispatches:
    idx = item["index"]
    name = item["name"]
    category = item["category"]
    print(f"[{idx:02d}/{total:02d}] Dispatching: {name} ({category})...")
    try:
        t0 = time.time()
        item["func"]()
        elapsed = time.time() - t0
        print(f"       ✅ Successfully delivered to {TARGET_RECIPIENT} in {elapsed:.2f}s")
        success_count += 1
    except Exception as exc:
        print(f"       ❌ Failed: {exc}")
        failed_count += 1

    # Brief delay between dispatches to allow Gmail SMTP to process smoothly
    time.sleep(0.8)

print("\n" + "=" * 70)
print(f"DISPATCH MISSION COMPLETE")
print(f"Total Attempted: {total}")
print(f"Delivered:       {success_count} / {total} (100% SUCCESS)" if failed_count == 0 else f"Failed: {failed_count}")
print(f"Target:          {TARGET_RECIPIENT}")
print(f"Time (IST):      {ist_str}")
print("=" * 70)
