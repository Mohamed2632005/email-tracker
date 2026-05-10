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
    <body style="font-family: Arial, sans-serif; color: #1a1a1a; max-width: 620px; margin: auto; padding: 20px;">

      <p>Salut Angelina ! 👋</p>

      <p>Je suis Camille, Influence Marketing Manager chez NYX Professional Makeup France. Je te contacte directement parce qu'on a un projet qui, j'en suis convaincue, pourrait vraiment te parler.</p>

      <p>On suit ton TikTok depuis un moment et franchement — 867K abonnés, 56 millions de likes, et tout ça construit en moins d'un an — c'est juste impressionnant. Mais ce qui nous a vraiment convaincues de t'écrire, c'est la façon dont tu parles de maquillage. T'as ce truc rare : tu testes, tu donnes ton vrai avis, et ta communauté te fait confiance pour ça. Et c'est exactement ce qu'on cherche.</p>

      <p><strong>Côté projet, voilà pourquoi on te contacte :</strong></p>

      <p>On a 3 produits qu'on veut vraiment pousser cet été et pour lesquels on cherche des créatrices capables de les tester honnêtement devant leur audience :</p>

      <ul>
        <li>💧 <strong>Le Fat Oil Lip Drip</strong> — notre huile à lèvres star, ultra brillante et hydratante, qui fait actuellement un carton aux US</li>
        <li>🖊️ <strong>L'Epic Ink Waterproof Liquid Eyeliner</strong> — précis, longue tenue 24h, le genre de produit parfait à tester en GRWM</li>
        <li>🌟 <strong>Le Buttermelt Bronzer</strong> — notre bronzer crémeux effet bonne mine qui buzze en ce moment sur les réseaux</li>
      </ul>

      <p>L'idée serait simple : on t'envoie les 3, tu les testes sur TikTok à ta façon (GRWM, tutoriel, avis honnête — t'es libre), et tu dis ce que t'en penses vraiment à ta commu. Pas de script, pas de discours marketing — juste toi et les produits.</p>

      <p><strong>Ce qu'on propose concrètement :</strong></p>

      <ul>
        <li>✅ Un colis de produits offerts en avant-première (~150€ de valeur)</li>
        <li>✅ 1 à 2 TikToks sponsorisés — 900€ par contenu validé</li>
        <li>✅ Un code promo exclusif pour ta communauté + 10% de commission sur chaque vente générée</li>
        <li>✅ Liberté créative totale, on ne touche pas à ton contenu</li>
      </ul>

      <p>Si ça te tente, on peut s'appeler 15-20 min cette semaine pour en parler tranquillement — ou si tu préfères tout par mail, aucun souci non plus !</p>

      <p style="text-align:center; margin: 30px 0;">
        <a href="{{click_url}}"
           style="background:#000; color:#fff; padding:14px 32px; text-decoration:none;
                  border-radius:4px; font-weight:bold; font-size:15px; display:inline-block;">
          Je suis intéressée →
        </a>
      </p>

      <p>Hâte d'avoir ton retour 🙂</p>

      <p>
        <strong>Camille Rousseau</strong><br>
        Influence Marketing Manager – NYX Professional Makeup France<br>
        <a href="mailto:camille.rousseau@nyxcosmetics.fr">camille.rousseau@nyxcosmetics.fr</a><br>
        +33 6 12 48 73 91<br>
        <a href="https://nyxcosmetics.fr">nyxcosmetics.fr</a> | @nyxcosmetics_fr
      </p>

    </body>
    </html>
    """

    send_tracked_email(
        destinataire="mohamed.toubi263@gmail.com",
        sujet="Collab NYX x toi — on a un projet pour cet été 🎀",
        contenu_html=contenu,
        campaign_id="campagne-mai-2026"
    )
