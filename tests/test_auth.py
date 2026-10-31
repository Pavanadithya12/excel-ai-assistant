import pytest
from app.models.user import User

def test_auth_workflow(client, db_session):
    email = "testuser@example.com"
    password = "SecurePassword123!"
    full_name = "Alex Tester"

    # 1. Registration
    reg_res = client.post("/api/auth/register", json={
        "email": email,
        "password": password,
        "full_name": full_name
    })
    assert reg_res.status_code == 201
    reg_data = reg_res.json()
    assert "Verification code" in reg_data["message"]
    user = db_session.query(User).filter(User.email == email).first()
    assert user is not None
    otp = user.otp_code
    assert len(otp) == 6

    # 2. Verify OTP
    verify_res = client.post("/api/auth/verify-otp", json={
        "email": email,
        "otp": otp
    })
    assert verify_res.status_code == 200
    token_data = verify_res.json()
    assert "access_token" in token_data
    token = token_data["access_token"]
    assert token_data["user"]["is_verified"] is True

    # 3. Login after verification
    login_res = client.post("/api/auth/login", json={
        "email": email,
        "password": password
    })
    assert login_res.status_code == 200
    assert "access_token" in login_res.json()

    # 4. Access protected /me endpoint
    headers = {"Authorization": f"Bearer {token}"}
    me_res = client.get("/api/auth/me", headers=headers)
    assert me_res.status_code == 200
    me_data = me_res.json()
    assert me_data["email"] == email
    assert me_data["full_name"] == full_name
