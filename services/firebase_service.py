import firebase_admin
from firebase_admin import credentials, firestore, storage
from config import Config

# Inicializa UMA única vez
if not firebase_admin._apps:
    cred = credentials.Certificate(Config.FIREBASE_CREDENTIALS)

    firebase_admin.initialize_app(
        cred,
        {
            "storageBucket": Config.FIREBASE_STORAGE_BUCKET
        }
    )

# Clientes globais
db = firestore.client()

# ⚠️ FORÇA O BUCKET PELO NOME (blindado)
bucket = storage.bucket(Config.FIREBASE_STORAGE_BUCKET)
