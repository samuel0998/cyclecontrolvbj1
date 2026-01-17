import os
from flask import Blueprint, jsonify, request
from datetime import datetime

from services.processing_service import ProcessingService
from services.storage_service import StorageService
from services.firebase_service import db

from config import Config

processing_bp = Blueprint(
    "processing",
    __name__,
    url_prefix="/api/processing"
)


@processing_bp.route("/faast", methods=["POST"])
def process_faast_file():
    """
    Recebe:
    - cycleId
    - path do CSV FAAST já baixado
    """

    data = request.json
    cycle_id = data["cycleId"]
    raw_file = data["filePath"]

    processed_files = ProcessingService.process_faast_csv(
        raw_file,
        cycle_id
    )

    created = 0

    for file in processed_files:

        storage_path = f"cycles/{cycle_id}/{file['fileName']}"

        StorageService.upload_cycle_file(
            file["localPath"],
            storage_path
        )

        db.collection("cycle_files").add({
            "cycleId": cycle_id,

            "aaLogin": file["aaLogin"],
            "fileName": file["fileName"],
            "storagePath": storage_path,

            "totalAddresses": file["totalAddresses"],
            "totalSkus": file["totalSkus"],

            "status": "PENDENTE",
            "assignedCounter": None,
            "assignedAt": None,

            "errorsFound": None,
            "finishedAt": None,

            "createdAt": datetime.utcnow().isoformat()
        })

        created += 1

    # Atualiza ciclo
    db.collection("cycles").document(cycle_id).update({
        "totalFiles": created
    })

    return jsonify({
        "message": "Processamento concluído",
        "filesCreated": created
    }), 200
