from datetime import timedelta
import os
from services.firebase_service import bucket


class StorageService:

    @staticmethod
    def upload_cycle_file(local_path: str, storage_path: str):
        """
        Faz upload de um arquivo local para o Firebase Storage
        """
        if not os.path.exists(local_path):
            raise FileNotFoundError(f"Arquivo não encontrado: {local_path}")

        blob = bucket.blob(storage_path)
        blob.upload_from_filename(local_path)

        print(f"☁️ Upload realizado: {storage_path}")

        return storage_path

    @staticmethod
    def generate_signed_url(storage_path, minutes=10):
        """
        Gera URL temporária para download
        """
        blob = bucket.blob(storage_path)

        if not blob.exists():
            raise Exception("Arquivo não encontrado no Storage")

        return blob.generate_signed_url(
            version="v4",
            expiration=timedelta(minutes=minutes),
            method="GET"
        )
