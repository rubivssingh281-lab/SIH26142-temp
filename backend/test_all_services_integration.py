import sys
import time
from pathlib import Path

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass
from dotenv import load_dotenv

backend_dir = Path(__file__).resolve().parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

load_dotenv(backend_dir / ".env")

from fastapi.testclient import TestClient
from app.main import app
from app.core.config import settings

client = TestClient(app)

def run_integration_tests():
    print("=" * 70)
    print("🛰️  भू DRISTI — Full Frontend & Backend Services Integration Suite")
    print("=" * 70)
    print(f"Base API:     http://localhost:8000/api")
    print(f"SMTP Server:  {settings.SMTP_HOST}:{settings.SMTP_PORT}")
    print(f"Sender Email: {settings.SMTP_FROM_EMAIL}")
    print("=" * 70)

    # 1. Dashboard
    print("\n[1/12] Testing GET /api/dashboard...")
    res = client.get("/api/dashboard")
    assert res.status_code == 200, res.text
    data = res.json()
    assert "stats" in data and "recent_job" in data
    print(f"  ✅ Dashboard OK (Total jobs: {data['stats']['total_jobs']}, GPU Utilization: {data['system_status']['gpu_cluster']['utilization_pct']}%)")

    # 2. Queue
    print("\n[2/12] Testing GET /api/queue...")
    res = client.get("/api/queue")
    assert res.status_code == 200, res.text
    data = res.json()
    assert "jobs" in data and "stats" in data
    print(f"  ✅ Queue OK ({len(data['jobs'])} jobs loaded, {data['stats']['processing']} active)")

    # 3. Projects
    print("\n[3/12] Testing GET /api/projects...")
    res = client.get("/api/projects?category=All")
    assert res.status_code == 200, res.text
    data = res.json()
    assert "projects" in data and len(data["projects"]) > 0
    print(f"  ✅ Projects OK ({len(data['projects'])} projects loaded)")

    # 4. Comparison & Validation
    print("\n[4/12] Testing GET /api/comparison & /api/validation...")
    res = client.get("/api/comparison/SR_v2_20240520_1030")
    assert res.status_code == 200, res.text
    comp = res.json()
    assert "crops" in comp and "metrics" in comp
    print(f"  ✅ Comparison OK ({len(comp['crops'])} analysis crops, {len(comp['metrics'])} metrics)")

    res = client.get("/api/validation/SR_v2_20240520_1030")
    assert res.status_code == 200, res.text
    val = res.json()
    assert "metrics" in val and "tasks" in val
    print(f"  ✅ Validation OK (PSNR: {val['metrics'][0]['value']}, Tasks: {len(val['tasks'])})")

    # 5. Settings roundtrip
    print("\n[5/12] Testing GET & PUT /api/settings...")
    res = client.get("/api/settings")
    assert res.status_code == 200, res.text
    s_data = res.json()
    assert "default_model" in s_data
    put_res = client.put("/api/settings", json={"priority": "high", "gpu_allocation": 4})
    assert put_res.status_code == 200, put_res.text
    assert put_res.json()["gpu_allocation"] == 4
    print("  ✅ Settings round-trip persisted successfully.")

    # 6. Job Estimation
    print("\n[6/12] Testing POST /api/jobs/estimate...")
    res = client.post("/api/jobs/estimate", json={"area_km2": 25.5})
    assert res.status_code == 200, res.text
    est = res.json()
    assert est["area_km2"] == 25.5
    print(f"  ✅ Job Estimate OK (Time: {est['estimated_time']}, Storage: {est['estimated_storage_gb']} GB)")

    # 7. Job Creation (JSON Frontend Wizard) + SMTP Queued Alert
    print("\n[7/12] Testing POST /api/jobs (New Job creation + Live SMTP Queue Notification)...")
    res = client.post(
        "/api/jobs",
        json={
            "project": "Ladakh Border Infrastructure",
            "job_name": "SR_v2_Ladakh_Sector_04",
            "satellite_source": "sentinel-2",
            "model": "gan",
            "target_resolution_m": 2.5,
            "bands": ["RGB", "NIR"],
            "aoi_coordinates": [[77.1, 34.2], [77.2, 34.3]],
        }
    )
    assert res.status_code == 201, res.text
    job_id = res.json()["job_id"]
    print(f"  ✅ Job created: {job_id} (Status: {res.json()['status']})")

    # 8. Complete Job & Dispatch Live SMTP Completion Alert
    print(f"\n[8/12] Testing POST /api/jobs/{job_id}/simulate-complete (Inference Complete + Live SMTP Completion Notification)...")
    res = client.post(f"/api/jobs/{job_id}/simulate-complete")
    assert res.status_code == 200, res.text
    assert res.json()["job"]["status"] == "completed"
    print(f"  ✅ Job {job_id} marked as completed & SMTP notification dispatched.")

    # 9. In-App Notifications Feed & Mark Read
    print("\n[9/12] Testing GET /api/notifications...")
    res = client.get("/api/notifications")
    assert res.status_code == 200, res.text
    notifs = res.json()
    assert len(notifs) > 0
    print(f"  ✅ In-App Notifications Feed OK ({len(notifs)} notifications, Latest: '{notifs[0]['title']}')")

    client.post("/api/notifications/read-all")
    res_after = client.get("/api/notifications")
    assert all(n["read"] for n in res_after.json())
    print("  ✅ Mark all notifications as read OK.")

    # 10. Live SMTP Channel Diagnostic Test
    print("\n[10/12] Testing POST /api/notifications/test (Live SMTP Diagnostic Channel Verification)...")
    res = client.post("/api/notifications/test", json={"email": "bhudhristi@gmail.com", "channel": "Email"})
    assert res.status_code == 200, res.text
    print(f"  ✅ Live SMTP Diagnostic Notification Sent: {res.json()['message']}")

    # 11. Report Generation and Live SMTP Dispatch with PDF Attachment
    print(f"\n[11/12] Testing POST /api/reports/validation/{job_id}/email (PDF Report Generation & SMTP Attachment Delivery)...")
    res = client.post(
        f"/api/reports/validation/{job_id}/email",
        json={"email": "bhudhristi@gmail.com"}
    )
    assert res.status_code == 200, res.text
    print(f"  ✅ Validation Report PDF dispatched via SMTP: {res.json()['message']} (File: {res.json()['filename']})")

    # 12. Authentication with OTP via SMTP
    print("\n[12/12] Testing Auth with OTP via SMTP (/api/auth/request-login-otp)...")
    res = client.post("/api/auth/request-login-otp", json={"email": "bhudhristi@gmail.com"})
    assert res.status_code == 200, res.text
    print(f"  ✅ Login OTP dispatched via SMTP: {res.json()['message']}")

    print("\n" + "=" * 70)
    print("🎉 ALL 12 INTEGRATION SERVICES & SMTP NOTIFICATIONS PASSED 100%!")
    print("=" * 70)

if __name__ == "__main__":
    run_integration_tests()
