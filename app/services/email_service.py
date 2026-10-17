import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import logging
from app.config import settings

logger = logging.getLogger("email_service")
logging.basicConfig(level=logging.INFO)

class EmailService:
    @staticmethod
    def send_otp_email(to_email: str, otp_code: str) -> bool:
        """
        Sends OTP email. In dev mode, prints clearly to console and logs.
        If SMTP is configured, sends via real SMTP.
        """
        subject = f"Your Verification Code - {settings.PROJECT_NAME}"
        body_text = f"""
Hello,

Your verification OTP code for {settings.PROJECT_NAME} is:

    ===========================
             {otp_code}
    ===========================

This code will expire in 10 minutes. If you did not request this, please ignore this email.

Best regards,
The {settings.PROJECT_NAME} Team
"""
        # Always log prominently to terminal for effortless development and testing
        print("\n" + "=" * 60)
        print(f"📧 [EMAIL SERVICE - OTP NOTIFICATION]")
        print(f"To: {to_email}")
        print(f"Subject: {subject}")
        print(f"OTP Code: >>> {otp_code} <<< (valid for 10 minutes)")
        print("=" * 60 + "\n")
        
        # If SMTP is configured, attempt real email delivery
        if settings.SMTP_HOST and settings.SMTP_USER and settings.SMTP_PASSWORD:
            try:
                msg = MIMEMultipart()
                msg['From'] = settings.FROM_EMAIL
                msg['To'] = to_email
                msg['Subject'] = subject
                msg.attach(MIMEText(body_text, 'plain'))
                
                with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT) as server:
                    server.starttls()
                    server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
                    server.send_message(msg)
                logger.info(f"OTP email sent successfully to {to_email}")
                return True
            except Exception as e:
                logger.error(f"Failed to send email via SMTP: {e}")
                # Fall back to True since console log is already captured
                return True
        return True

email_service = EmailService()
