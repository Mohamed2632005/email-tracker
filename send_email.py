import base64
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
    logo_path = os.environ.get("NYX_LOGO_PATH", "img/Capture d'écran 2026-05-10 142715.png")
    with open(logo_path, "rb") as f:
        logo_b64 = base64.b64encode(f.read()).decode()

    contenu = f"""
    <html>
    <body style="font-family: Arial, sans-serif; color: #1a1a1a; max-width: 620px; margin: auto; padding: 0;">

      <div style="background:#000; text-align:center; padding: 20px 0;">
        <img src="data:image/png;base64,{logo_b64}" width="300" alt="NYX Professional Makeup" style="display:block; margin:auto;" />
      </div>

      <div style="padding: 30px 20px;">

        <p>Salut Angelina ! 👋</p>

        <p>Je suis Camille, Influence Marketing Manager chez NYX Professional Makeup France.</p>

        <p>On suit ton TikTok depuis un moment et on aimerait te proposer une collab rémunérée cet été autour de quelques-uns de nos produits phares. L'idée : tu les testes à ta façon, on ne touche pas à ton contenu.</p>

        <p>Si ça t'intéresse, tous les détails sont ici : <a href="{{{{click_url}}}}">voir la proposition complète</a></p>

        <p>Hâte d'avoir ton retour 🙂</p>

        <p>
          <strong>Camille Rousseau</strong><br>
          Influence Marketing Manager – NYX Professional Makeup France<br>
          <a href="mailto:camille.rousseau@nyxcosmetics.fr">camille.rousseau@nyxcosmetics.fr</a><br>
          +33 6 12 48 73 91
        </p>

      </div>

    </body>
    </html>
    """

    send_tracked_email(
        destinataire="mohamed.toubi263@gmail.com",
        sujet="Collab NYX x toi — on a un projet pour cet été 🎀",
        contenu_html=contenu,
        campaign_id="campagne-mai-2026"
    )
