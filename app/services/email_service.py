import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import logging
from app.config import settings

logger = logging.getLogger("email_service")
logging.basicConfig(level=logging.INFO)

class EmailService:
    @staticmethod
    def send_otp_email(to_email: str, otp_code: str) -> dict:
        """
        Dispatches a 6-digit OTP verification code to the user's email address.
        Uses TLS/SSL SMTP (e.g. Gmail, Outlook, AWS SES, Brevo, or custom SMTP).
        Also prints prominent development logs to the server terminal.
        Returns a dictionary with delivery diagnostics.
        """
        subject = f"Your Verification OTP Code: {otp_code} - {settings.PROJECT_NAME}"
        
        # Plain text fallback
        body_text = f"""Hello,

Your verification OTP code for {settings.PROJECT_NAME} is:

    ===========================
             {otp_code}
    ===========================

This 6-digit code is valid for 10 minutes.
Copy and paste this code into the login verification prompt to access your workspace.

If you did not request this verification code, please ignore this email.

Best regards,
The {settings.PROJECT_NAME} Team
"""

        # Branded Modern Red & White HTML Email
        body_html = f"""<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <title>Your Verification Code</title>
</head>
<body style="margin: 0; padding: 0; background-color: #f8fafc; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; color: #1e293b;">
  <table role="presentation" width="100%" cellspacing="0" cellpadding="0" style="background-color: #f8fafc; padding: 40px 15px;">
    <tr>
      <td align="center">
        <table role="presentation" width="100%" style="max-width: 520px; background-color: #ffffff; border-radius: 12px; border: 1px solid #f3c5ce; box-shadow: 0 10px 25px -5px rgba(128, 0, 32, 0.08); overflow: hidden;">
          <!-- Header Banner -->
          <tr>
            <td style="background: linear-gradient(135deg, #9b1137 0%, #800020 100%); padding: 28px 30px; text-align: center;">
              <h1 style="margin: 0; color: #ffffff; font-size: 22px; font-weight: 700; letter-spacing: -0.5px;">Excel AI Assistant</h1>
              <p style="margin: 6px 0 0; color: #fce7f3; font-size: 13px;">Secure Two-Factor Authentication</p>
            </td>
          </tr>
          <!-- Content Body -->
          <tr>
            <td style="padding: 35px 30px;">
              <p style="margin: 0 0 16px; font-size: 15px; line-height: 1.5; color: #334155;">Hello,</p>
              <p style="margin: 0 0 24px; font-size: 15px; line-height: 1.5; color: #334155;">
                We received a sign-in or registration request for <b>{to_email}</b>. Use the 6-digit verification code below to complete your authentication:
              </p>
              
              <!-- OTP Box -->
              <div style="background-color: #fdf2f4; border: 2px dashed #800020; border-radius: 10px; padding: 22px; text-align: center; margin: 25px 0;">
                <span style="font-family: 'Courier New', Courier, monospace; font-size: 34px; font-weight: 800; letter-spacing: 8px; color: #800020; display: inline-block;">
                  {otp_code}
                </span>
                <p style="margin: 10px 0 0; font-size: 12px; color: #5a0017; font-weight: 600;">
                  Code expires in 10 minutes
                </p>
              </div>

              <p style="margin: 0 0 12px; font-size: 13.5px; line-height: 1.5; color: #64748b;">
                Copy and enter this code in the login verification screen to access your spreadsheet intelligence dashboard.
              </p>
              <p style="margin: 0; font-size: 13px; line-height: 1.5; color: #94a3b8;">
                If you did not request this login code, you can safely ignore this email.
              </p>
            </td>
          </tr>
          <!-- Footer -->
          <tr>
            <td style="background-color: #f8fafc; border-top: 1px solid #f1f5f9; padding: 18px 30px; text-align: center; font-size: 12px; color: #94a3b8;">
              &copy; {settings.PROJECT_NAME} • Secure Relational Spreadsheet Analytics
            </td>
          </tr>
        </table>
      </td>
    </tr>
  </table>
</body>
</html>
"""

        # Prominent console logging (ASCII-safe for all Windows / Linux terminals)
        try:
            print("\n" + "=" * 65)
            print("[EMAIL SERVICE - OTP NOTIFICATION]")
            print(f"To: {to_email}")
            print(f"Subject: {subject}")
            print(f"OTP Code: >>> {otp_code} <<< (valid for 10 minutes)")
            if not (settings.SMTP_HOST and settings.SMTP_USER and settings.SMTP_PASSWORD):
                print("[TIP] Set SMTP_HOST, SMTP_USER, SMTP_PASSWORD in .env to deliver real emails to inbox!")
            print("=" * 65 + "\n")
        except Exception:
            pass
        
        # Real SMTP Delivery
        if settings.SMTP_HOST and settings.SMTP_USER and settings.SMTP_PASSWORD:
            try:
                msg = MIMEMultipart("alternative")
                from_addr = settings.FROM_EMAIL or settings.SMTP_USER
                msg['From'] = f"{settings.PROJECT_NAME} <{from_addr}>"
                msg['To'] = to_email
                msg['Subject'] = subject
                msg.attach(MIMEText(body_text, 'plain'))
                msg.attach(MIMEText(body_html, 'html'))
                
                # Port 465 (SSL) vs Port 587 (STARTTLS)
                if settings.SMTP_PORT == 465:
                    with smtplib.SMTP_SSL(settings.SMTP_HOST, settings.SMTP_PORT, timeout=10) as server:
                        server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
                        server.send_message(msg)
                else:
                    with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT, timeout=10) as server:
                        server.starttls()
                        server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
                        server.send_message(msg)

                logger.info(f"Real OTP email delivered via SMTP to {to_email}")
                return {
                    "success": True,
                    "delivered_via_smtp": True,
                    "message": f"Verification code sent to {to_email} inbox.",
                    "error_detail": None
                }
            except Exception as e:
                err_msg = str(e)
                logger.error(f"Failed to deliver email via SMTP: {err_msg}")
                return {
                    "success": False,
                    "delivered_via_smtp": False,
                    "message": f"SMTP delivery failed ({err_msg}).",
                    "error_detail": err_msg
                }
        else:
            reason = "SMTP_PASSWORD is empty in .env" if not settings.SMTP_PASSWORD else "SMTP settings incomplete in .env"
            logger.info(f"{reason}. Console OTP logged.")
            return {
                "success": True,
                "delivered_via_smtp": False,
                "message": f"Real email delivery paused ({reason}).",
                "error_detail": reason
            }

email_service = EmailService()
