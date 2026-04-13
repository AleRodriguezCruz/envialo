import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from app.core.config import settings

class EmailService:
    async def send_download_link(
        self,
        to_email: str,
        download_url: str,
        filename: str,
        message: str | None = None,
        expires_at: str | None = None
    ) -> bool:
        try:
            # 1. Crear el contenedor del mensaje
            email_msg = MIMEMultipart()
            email_msg["From"] = f"{settings.SMTP_FROM_NAME} <{settings.SMTP_USER}>"
            email_msg["To"] = to_email
            email_msg["Subject"] = f"📦 {filename} — Archivo compartido contigo"

            # 2. Diseño HTML del correo
            html_content = f"""
            <div style="font-family: sans-serif; max-width: 600px; margin: 0 auto; padding: 20px; border: 1px solid #eee; border-radius: 10px;">
                <h2 style="color: #6366f1;">📦 Te han enviado un archivo</h2>
                {f"<p style='background: #f3f4f6; padding: 10px; border-left: 4px solid #6366f1;'><em>{message}</em></p>" if message else ""}
                <p>Puedes descargar <strong>{filename}</strong> haciendo clic en el botón:</p>
                <div style="text-align: center; margin: 30px 0;">
                    <a href="{download_url}" 
                       style="background: #6366f1; color: white; padding: 14px 28px; text-decoration: none; border-radius: 8px; font-weight: bold; display: inline-block;">
                        Descargar archivo
                    </a>
                </div>
                {f"<p style='color: #ef4444; font-size: 0.85rem;'>⏰ Expira: {expires_at}</p>" if expires_at else ""}
                <p style="color: #888; font-size: 0.8rem; margin-top: 30px; border-top: 1px solid #eee; padding-top: 10px;">
                    Enviado con <strong>Envialo</strong>
                </p>
            </div>
            """
            email_msg.attach(MIMEText(html_content, "html"))

            # 3. Envío mediante el servidor de Google
            with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT) as server:
                server.starttls()  # Activar cifrado de seguridad
                server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
                server.send_message(email_msg)
            
            return True

        except Exception as e:
            print(f"[EmailService] Error SMTP: {str(e)}")
            return False

email_service = EmailService()