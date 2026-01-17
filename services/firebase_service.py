import json
import firebase_admin
from firebase_admin import credentials, firestore, storage
from config import Config

# Inicializa UMA única vez
if not firebase_admin._apps:
    if not Config.FIREBASE_CREDENTIALS_JSON:
        raise RuntimeError("FIREBASE_CREDENTIALS_JSON não definido")

    cred_dict = json.loads(Config.FIREBASE_CREDENTIALS_JSON)

    cred = credentials.Certificate(cred_dict)

    firebase_admin.initialize_app(
        cred,
        {
            "storageBucket": Config.FIREBASE_STORAGE_BUCKET
        }
    )

# Clientes globais
db = firestore.client()
bucket = storage.bucket()
