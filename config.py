import os
import json
from datetime import timedelta
from dotenv import load_dotenv

# Carrega .env apenas em ambiente local
load_dotenv()


class Config:
    # =========================
    # FLASK
    # =========================
    SECRET_KEY = os.getenv("SECRET_KEY", "cycle-control-secret")

    # =========================
    # AMBIENTE
    # =========================
    FLASK_ENV = os.getenv("FLASK_ENV", "development")
    DEBUG = FLASK_ENV == "development"

    # =========================
    # TURNOS / CICLOS
    # =========================
    CYCLE_INTERVAL_HOURS = int(os.getenv("CYCLE_INTERVAL_HOURS", 12))
    TIMEZONE = os.getenv("TIMEZONE", "America/Sao_Paulo")

    # =========================
    # PATHS DO SISTEMA (LOCAL)
    # =========================
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))

    UPLOAD_FOLDER = os.path.join(BASE_DIR, "uploads")
    RAW_FOLDER = os.path.join(UPLOAD_FOLDER, "raw")
    PROCESSED_FOLDER = os.path.join(UPLOAD_FOLDER, "processed")

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
    # 🔥 FIREBASE (RAILWAY READY)
    # =========================
    # JSON completo do Service Account (Railway)
    FIREBASE_CREDENTIALS_JSON = os.getenv("FIREBASE_CREDENTIALS_JSON")

    # Bucket
    FIREBASE_STORAGE_BUCKET = os.getenv(
        "FIREBASE_STORAGE_BUCKET",
        "cyclecontrol-af711.firebasestorage.app"
    )

    # =========================
    # AUTH / PERFIS
    # =========================
    ROLES = {
        "ADMIN": "admin",
        "SUPERVISOR": "supervisor",
        "CONTADOR": "contador"
    }

    # =========================
    # SESSION
    # =========================
    PERMANENT_SESSION_LIFETIME = timedelta(hours=12)
