import os
import smtplib
import uuid
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from dotenv import load_dotenv

load_dotenv("valeures.env")

# --- Credentials lus depuis .env (jamais dans le code) ---
GMAIL_ADDRESS     = os.environ["GMAIL_ADDRESS"]
GMAIL_PASSWORD    = os.environ["GMAIL_PASSWORD"]
TRACKING_BASE_URL = os.environ.get("TRACKING_URL", "http://localhost:5000/pixel.gif")


def send_tracked_email(destinataire: str, sujet: str, contenu_html: str, campaign_id: str = None) -> bool:
    if campaign_id is None:
        campaign_id = str(uuid.uuid4())[:8]  # ID court aléatoire si non fourni

    tracking_url = f"{TRACKING_BASE_URL}?id={campaign_id}"

    # Pixel injecté automatiquement en fin de body
    html_final = contenu_html + f"""
    <img src="{tracking_url}" width="1" height="1"
         style="display:none; border:0;" alt="" />
    """

    msg = MIMEMultipart("alternative")
    msg["Subject"] = sujet
    msg["From"]    = GMAIL_ADDRESS
    msg["To"]      = destinataire
    msg.attach(MIMEText(html_final, "html"))

    try:
        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            server.login(GMAIL_ADDRESS, GMAIL_PASSWORD)
            server.sendmail(GMAIL_ADDRESS, destinataire, msg.as_string())
        print(f"✓ Email envoyé à {destinataire} (campagne : {campaign_id})")
        return True
    except smtplib.SMTPAuthenticationError:
        print("✗ Authentification refusée — vérifie l'adresse et le mot de passe d'application Google")
        return False
    except smtplib.SMTPException as e:
        print(f"✗ Erreur SMTP : {e}")
        return False


if __name__ == "__main__":
    contenu = """
    <html>
    <body style="font-family: Arial, sans-serif;">
      <h2>Bonjour !</h2>
      <p>Voici le contenu de mon email.</p>
      <p>Cordialement,<br>Mon Nom</p>
    </body>
    </html>
    """

    send_tracked_email(
        destinataire="mohamed.toubi263@gmail.com",
        sujet="Ma newsletter",
        contenu_html=contenu,
        campaign_id="campagne-mai-2026"
    )
