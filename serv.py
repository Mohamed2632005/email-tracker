import io
import os
import csv
import logging
import datetime
from flask import Flask, request, send_file, Response
from dotenv import load_dotenv

load_dotenv("valeures.env")

# --- Configuration ---
PORT     = int(os.environ.get("PORT", 5000))
LOG_FILE = os.environ.get("LOG_FILE", "tracking_log.csv")

# --- Logging console ---
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
logger = logging.getLogger(__name__)

# --- Création du fichier CSV si absent ---
if not os.path.exists(LOG_FILE):
    with open(LOG_FILE, "w", newline="", encoding="utf-8") as f:
        csv.writer(f).writerow(["date", "campagne", "ip", "user_agent"])

# GIF 1x1 pixel transparent (binaire fixe, inutile de le recalculer)
GIF_PIXEL = bytes([
    0x47, 0x49, 0x46, 0x38, 0x39, 0x61, 0x01, 0x00,
    0x01, 0x00, 0x80, 0x00, 0x00, 0xFF, 0xFF, 0xFF,
    0x00, 0x00, 0x00, 0x21, 0xF9, 0x04, 0x00, 0x00,
    0x00, 0x00, 0x00, 0x2C, 0x00, 0x00, 0x00, 0x00,
    0x01, 0x00, 0x01, 0x00, 0x00, 0x02, 0x02, 0x44,
    0x01, 0x00, 0x3B
])

app = Flask(__name__)


@app.route("/pixel.gif")
def pixel():
    forwarded  = request.headers.get("X-Forwarded-For", "")
    ip         = forwarded.split(",")[0].strip() if forwarded else request.remote_addr
    user_agent = request.headers.get("User-Agent", "inconnu")
    campaign   = request.args.get("id", "inconnu")
    now        = datetime.datetime.now()

    # Enregistrement dans le CSV
    with open(LOG_FILE, "a", newline="", encoding="utf-8") as f:
        csv.writer(f).writerow([now.isoformat(), campaign, ip, user_agent])

    logger.info(f"campagne={campaign} | IP={ip}")

    # Cache désactivé pour forcer le rechargement à chaque ouverture
    response = send_file(io.BytesIO(GIF_PIXEL), mimetype="image/gif")
    response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate"
    response.headers["Pragma"]        = "no-cache"
    return response


_ERROR_PAGE = """<!DOCTYPE html>
<html lang="fr">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Erreur</title>
  <style>
    * { margin: 0; padding: 0; box-sizing: border-box; }
    body { font-family: Arial, sans-serif; background: #f4f4f4;
           display: flex; align-items: center; justify-content: center; min-height: 100vh; }
    .card { background: #fff; padding: 40px 50px; border-radius: 8px;
            box-shadow: 0 2px 12px rgba(0,0,0,.1); text-align: center; max-width: 420px; width: 90%; }
    .icon { font-size: 48px; margin-bottom: 16px; }
    h1 { font-size: 1.3em; color: #c0392b; margin-bottom: 10px; }
    p  { color: #555; line-height: 1.6; }
  </style>
</head>
<body>
  <div class="card">
    <div class="icon">⚠️</div>
    <h1>Une erreur est survenue</h1>
    <p>Le lien est temporairement indisponible.<br>Veuillez réessayer plus tard.</p>
  </div>
</body>
</html>"""


@app.route("/click")
def click():
    forwarded  = request.headers.get("X-Forwarded-For", "")
    ip         = forwarded.split(",")[0].strip() if forwarded else request.remote_addr
    user_agent = request.headers.get("User-Agent", "inconnu")
    campaign   = request.args.get("id", "inconnu")
    now        = datetime.datetime.now()

    with open(LOG_FILE, "a", newline="", encoding="utf-8") as f:
        csv.writer(f).writerow([now.isoformat(), campaign, ip, user_agent, "click"])

    logger.info(f"CLICK campagne={campaign} | IP={ip}")

    return Response(_ERROR_PAGE, status=200, mimetype="text/html")


if __name__ == "__main__":
    logger.info(f"Serveur de tracking démarré sur le port {PORT}")
    app.run(host="0.0.0.0", port=PORT, debug=False)
