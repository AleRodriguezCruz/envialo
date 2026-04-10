# =============================================================================
# email_service.py — Servicio de envío de correos con Resend
# Envía el link de descarga al destinatario por email
# =============================================================================
import resend
from app.core.config import settings

resend.api_key = settings.RESEND_API_KEY


class EmailService:

    # -------------------------------------------------------------------------
    # ENVIAR correo con el link de descarga
    # -------------------------------------------------------------------------
    async def send_download_link(
        self,
        to_email: str,
        download_url: str,
        filename: str,
        message: str | None = None,
        expires_at: str | None = None
    ) -> bool:
        try:
            html_content = f"""
            <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
                <h2 style="color: #6366f1;">📦 Te han enviado un archivo</h2>

                {"<p><em>" + message + "</em></p>" if message else ""}

                <p>Puedes descargar <strong>{filename}</strong> haciendo clic en el botón:</p>

                <a href="{download_url}"
                   style="display: inline-block; padding: 12px 24px;
                          background: #6366f1; color: white;
                          text-decoration: none; border-radius: 8px;
                          font-weight: bold;">
                    Descargar archivo
                </a>

                {"<p style='color: #888; font-size: 0.85rem;'>⏰ Expira: " + expires_at + "</p>" if expires_at else ""}

                <p style="color: #888; font-size: 0.8rem;">
                    Enviado con <a href="http://localhost:8000" style="color: #6366f1;">Envialo</a>
                </p>
            </div>
            """

            resend.Emails.send({
                "from": settings.RESEND_FROM_EMAIL,
                "to": to_email,
                "subject": f"📦 {filename} — Archivo compartido contigo",
                "html": html_content
            })
            return True

        except Exception as e:
            print(f"[EmailService] Error al enviar correo: {str(e)}")
            return False


# Instancia global
email_service = EmailService()