import io
import os
import csv
import logging
import datetime
from flask import Flask, request, send_file
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


if __name__ == "__main__":
    logger.info(f"Serveur de tracking démarré sur le port {PORT}")
    app.run(host="0.0.0.0", port=PORT, debug=False)
