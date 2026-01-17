import json
import firebase_admin
from firebase_admin import credentials, firestore, storage
from config import Config

if not firebase_admin._apps:

    # 🔥 PRODUÇÃO (Railway)
    if Config.FIREBASE_CREDENTIALS_JSON:
        cred_dict = json.loads(Config.FIREBASE_CREDENTIALS_JSON)
        cred = credentials.Certificate(cred_dict)

    # 🔥 LOCAL
    else:
        cred = credentials.Certificate(Config.FIREBASE_CREDENTIALS_FILE)

    firebase_admin.initialize_app(
        cred,
        {"storageBucket": Config.FIREBASE_STORAGE_BUCKET}
    )

db = firestore.client()
bucket = storage.bucket()
