from services.firebase_service import bucket


class StorageService:

    @staticmethod
    def upload_cycle_file(local_path, storage_path):
        blob = bucket.blob(storage_path)
        blob.upload_from_filename(local_path)

        return blob.public_url
