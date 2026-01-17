import os
from datetime import timedelta
from dotenv import load_dotenv

# Carrega .env apenas local
load_dotenv()


class Config:
    # =========================
    # FLASK
    # =========================
    SECRET_KEY = os.getenv("SECRET_KEY", "cycle-control-secret")

    FLASK_ENV = os.getenv("FLASK_ENV", "development")
    DEBUG = FLASK_ENV == "development"

    # =========================
    # CICLOS
    # =========================
    CYCLE_INTERVAL_HOURS = int(os.getenv("CYCLE_INTERVAL_HOURS", 12))
    TIMEZONE = os.getenv("TIMEZONE", "America/Sao_Paulo")

    # =========================
    # PATH BASE
    # =========================
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))

    # =========================
    # FAAST
    # =========================
    FAAST_BASE_URL = "https://faast.amazon.com/web/inventory/searchAudit"

    FAAST_DEFAULT_PARAMS = {
        "adjustmentType": "RECEIVE",
        "inventoryType": "PRIME_SELLABLE",
        "userId": "All",
        "action": "search#result"
    }

    FAAST_DOWNLOAD_FILENAME = "inventoryAudit_VBJ1"

    # =========================
    # 🔥 FIREBASE (DUAL MODE)
    # =========================

    # LOCAL → arquivo json
    FIREBASE_CREDENTIALS_FILE = os.getenv(
        "FIREBASE_CREDENTIALS",
        os.path.join(BASE_DIR, "firebase_key.json")
    )

    # PRODUÇÃO (Railway) → variável de ambiente
    FIREBASE_CREDENTIALS_JSON = os.getenv("FIREBASE_CREDENTIALS_JSON")

    FIREBASE_STORAGE_BUCKET = "cyclecontrol-af711.firebasestorage.app"

    # =========================
    # AUTH
    # =========================
    ROLES = {
        "ADMIN": "admin",
        "SUPERVISOR": "supervisor",
        "CONTADOR": "contador"
    }

    PERMANENT_SESSION_LIFETIME = timedelta(hours=12)
