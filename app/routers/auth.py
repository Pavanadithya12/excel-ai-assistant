import logging
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)

from app.database import get_db
from app.models.user import User
from app.models.excel_file import ExcelFile
from app.models.chat import ChatSession
from app.models.history import AnalysisHistory
from app.schemas.auth import (
    UserSignUpRequest, UserSignInRequest, VerifyOTPRequest, ResendOTPRequest,
    Token, UserProfileResponse, UserSummary
)
from app.services.auth_service import auth_service, get_current_user
from app.services.email_service import email_service

router = APIRouter(prefix="/api/auth", tags=["Authentication & User Management"])

@router.post("/register", response_model=dict, status_code=status.HTTP_201_CREATED)
def register_user(request: UserSignUpRequest, db: Session = Depends(get_db)):
    """
    Step 1: Sign up user with email, name, password.
    Generates and sends a 6-digit Email OTP.
    """
    existing_user = db.query(User).filter(User.email == request.email).first()
    if existing_user:
        if existing_user.is_verified:
            raise HTTPException(status_code=400, detail="An account with this email already exists.")
        # User exists but unverified: regenerate OTP
        user = existing_user
        user.full_name = request.full_name
        user.hashed_password = auth_service.hash_password(request.password)
    else:
        user = User(
            email=request.email,
            full_name=request.full_name,
            hashed_password=auth_service.hash_password(request.password),
            is_active=True,
            is_verified=False
        )
        db.add(user)

    # Generate OTP
    otp = auth_service.generate_otp()
    user.otp_code = otp
    user.otp_expires_at = datetime.utcnow() + timedelta(minutes=10)
    db.commit()

    # Send Email OTP directly to Gmail inbox
    delivery = email_service.send_otp_email(user.email, otp)
    if not delivery.get("delivered_via_smtp", False):
        logger.warning(f"SMTP delivery note for {user.email}: {delivery.get('message')}")

    return {
        "message": f"Verification code sent to {user.email}! Please check your Gmail inbox, copy the 6-digit code, and enter it below.",
        "email": user.email
    }

@router.post("/verify-otp", response_model=Token)
def verify_otp(request: VerifyOTPRequest, db: Session = Depends(get_db)):
    """
    Step 2: Verify Email OTP.
    Activates account, issues JWT Access Token.
    """
    user = db.query(User).filter(User.email == request.email).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found.")

    if not user.otp_code or user.otp_code != request.otp.strip():
        raise HTTPException(status_code=400, detail="Invalid verification OTP.")

    if user.otp_expires_at and datetime.utcnow() > user.otp_expires_at:
        raise HTTPException(status_code=400, detail="Verification OTP has expired. Please request a new one.")

    # Account Activated
    user.is_verified = True
    user.otp_code = None
    user.otp_expires_at = None
    db.commit()
    db.refresh(user)

    # Generate JWT
    token_str = auth_service.create_access_token({"sub": user.email, "user_id": user.id})
    return {
        "access_token": token_str,
        "token_type": "bearer",
        "user": user
    }

@router.post("/resend-otp", response_model=dict)
def resend_otp(request: ResendOTPRequest, db: Session = Depends(get_db)):
    """Resends a fresh OTP code to user's email"""
    user = db.query(User).filter(User.email == request.email).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found.")

    otp = auth_service.generate_otp()
    user.otp_code = otp
    user.otp_expires_at = datetime.utcnow() + timedelta(minutes=10)
    db.commit()

    email_service.send_otp_email(user.email, otp)
    return {
        "message": f"Fresh verification OTP code sent to {user.email}! Please check your Gmail inbox.",
        "email": user.email
    }

@router.post("/login", response_model=Token)
def login(request: UserSignInRequest, db: Session = Depends(get_db)):
    """
    Authenticate user credentials (email & password).
    Direct Login: NEVER generates or asks for an OTP on login.
    Immediately verifies password and returns JWT access token.
    """
    user = db.query(User).filter(User.email == request.email).first()
    if not user or not auth_service.verify_password(request.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid email or password.")

    # Ensure account is active for direct login
    if not user.is_verified:
        user.is_verified = True
        user.otp_code = None
        db.commit()

    # Immediate Direct Login — issues JWT session token with NO OTP
    token_str = auth_service.create_access_token({"sub": user.email, "user_id": user.id})
    return {
        "access_token": token_str,
        "token_type": "bearer",
        "user": user
    }

@router.get("/me", response_model=UserProfileResponse)
def get_user_profile(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Returns authenticated user's profile and analytics stats.
    """
    files_count = db.query(ExcelFile).filter(ExcelFile.user_id == current_user.id).count()
    chats_count = db.query(ChatSession).filter(ChatSession.user_id == current_user.id).count()
    history_count = db.query(AnalysisHistory).filter(AnalysisHistory.user_id == current_user.id).count()

    return {
        "id": current_user.id,
        "email": current_user.email,
        "full_name": current_user.full_name,
        "is_active": current_user.is_active,
        "is_verified": current_user.is_verified,
        "created_at": current_user.created_at,
        "total_files_uploaded": files_count,
        "total_chats": chats_count,
        "total_analyses": history_count
    }
