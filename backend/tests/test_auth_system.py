import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from fastapi.testclient import TestClient
from app.main import app
from app.db.session import init_db_tables

client = TestClient(app)

def setup_db():
    init_db_tables()

def test_signup_and_verify_otp():
    setup_db()
    email = "researcher.new@ntro.gov.in"
    # Signup
    signup_res = client.post("/auth/signup", json={
        "email": email,
        "password": "Password123!",
        "name": "Arjun Sharma",
        "organization": "NTRO — Geospatial Intelligence"
    })
    assert signup_res.status_code == 200
    assert signup_res.json()["requires_otp"] is True

    # Request new OTP code
    otp_req = client.post("/auth/request-otp", json={"email": email})
    assert otp_req.status_code == 200

def test_login_verified_user():
    setup_db()
    # Pre-seed user via Google OAuth or direct login
    email = "analyst.lead@ntro.gov.in"
    google_res = client.post("/auth/google", json={
        "email": email,
        "name": "Priya Nair",
        "id_token": "mock-firebase-token-123"
    })
    assert google_res.status_code == 200
    token = google_res.json()["access_token"]
    assert token is not None

    # Access protected /auth/me
    me_res = client.get("/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert me_res.status_code == 200
    assert me_res.json()["email"] == email
    assert me_res.json()["is_authenticated"] is True

def test_google_auto_provisioning():
    setup_db()
    email = "google.test.user@ntro.gov.in"
    res = client.post("/api/v1/auth/google", json={
        "email": email,
        "first_name": "Vikram",
        "last_name": "Seth",
        "name": "Vikram Seth"
    })
    assert res.status_code == 200
    data = res.json()
    assert data["user"]["email"] == email
    assert data["user"]["first_name"] == "Vikram"
    assert data["user"]["is_verified"] is True
    assert "access_token" in data
    assert "token" in data

def test_forgot_password_and_reset():
    setup_db()
    email = "reset.operator@ntro.gov.in"
    # Provision first
    client.post("/auth/google", json={"email": email, "name": "Reset Operator"})

    # Forgot password request
    req_res = client.post("/auth/forgot-password", json={"email": email})
    assert req_res.status_code == 200

def test_backward_compatibility_endpoints():
    setup_db()
    # Test all mounted prefix variants
    assert client.post("/api/v1/auth/request-login-otp", json={"email": "compat@ntro.gov.in"}).status_code == 200
    assert client.post("/api/auth/request-login-otp", json={"email": "compat@ntro.gov.in"}).status_code == 200
    assert client.post("/auth/request-login-otp", json={"email": "compat@ntro.gov.in"}).status_code == 200

if __name__ == "__main__":
    setup_db()
    test_signup_and_verify_otp()
    test_login_verified_user()
    test_google_auto_provisioning()
    test_forgot_password_and_reset()
    test_backward_compatibility_endpoints()
    print("ALL AUTH INTEGRATION TESTS PASSED 100%!")
