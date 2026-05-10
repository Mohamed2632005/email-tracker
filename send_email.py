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
CLICK_BASE_URL    = os.environ.get("CLICK_URL",    "http://localhost:5000/click")


def send_tracked_email(destinataire: str, sujet: str, contenu_html: str, campaign_id: str = None) -> bool:
    if campaign_id is None:
        campaign_id = str(uuid.uuid4())[:8]

    pixel_url = f"{TRACKING_BASE_URL}?id={campaign_id}"
    click_url = f"{CLICK_BASE_URL}?id={campaign_id}"

    # Remplace le placeholder {{click_url}} dans le template HTML par le vrai lien tracké
    contenu_html = contenu_html.replace("{{click_url}}", click_url)

    # Pixel ouverture injecté en fin de body
    html_final = contenu_html + f"""
    <img src="{pixel_url}" width="1" height="1"
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
    <body style="font-family: Arial, sans-serif; color: #1a1a1a; max-width: 620px; margin: auto; padding: 0;">

      <div style="background:#c8a96e; text-align:center; padding: 18px 0;">
        <span style="font-size:22px; font-weight:bold; color:#fff; letter-spacing:2px;">ÉCLAT STUDIO</span>
        <div style="font-size:11px; color:#fff; letter-spacing:1px; margin-top:4px;">Influence &amp; Brand Partnerships</div>
      </div>

      <div style="padding: 32px 28px;">

        <p>Bonjour,</p>

        <p>Je suis Sophie Marchand, responsable partenariats chez <strong>Éclat Studio</strong>, une agence spécialisée dans les collaborations entre créateurs de contenu et marques beauté/lifestyle.</p>

        <p>Nous suivons votre travail depuis plusieurs mois et nous aimerions vous proposer une collaboration rémunérée cet été. Le concept est simple : liberté créative totale, vous testez les produits à votre façon.</p>

        <p>Tous les détails de la proposition sont disponibles ici :<br>
        <a href="{{click_url}}" style="color:#c8a96e; font-weight:bold;">voir la proposition complète</a></p>

        <p>Vous pouvez également consulter notre site pour en savoir plus sur notre agence :<br>
        <a href="{{click_url}}" style="color:#c8a96e;">www.eclat-studio.fr</a></p>

        <p>N'hésitez pas à me répondre directement si vous avez des questions.</p>

        <p>Cordialement,</p>

        <p>
          <strong>Sophie Marchand</strong><br>
          Responsable Partenariats — Éclat Studio<br>
          <a href="mailto:s.marchand@eclat-studio.fr" style="color:#c8a96e;">s.marchand@eclat-studio.fr</a><br>
          +33 6 27 84 13 50
        </p>

      </div>

      <div style="background:#f5f5f5; text-align:center; padding:12px; font-size:11px; color:#999;">
        Éclat Studio — 14 rue des Acacias, 75017 Paris
      </div>

    </body>
    </html>
    """

    send_tracked_email(
        destinataire="mohamed.toubi263@gmail.com",
        sujet="Proposition de partenariat — Éclat Studio",
        contenu_html=contenu,
        campaign_id="campagne-mai-2026"
    )
