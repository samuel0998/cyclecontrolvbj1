from datetime import datetime
from services.faast_service import FaastService
from services.processing_service import ProcessingService
from services.firebase_service import bucket
from services.firebase_service import db

from utils.date_utils import get_current_cycle_window
from config import Config


def run_cycle_job():

    from_date, to_date = get_current_cycle_window()

    # 1️⃣ Criar ciclo
    cycle_ref = db.collection("cycles").add({
        "shift": f"{from_date.strftime('%d/%m')} - {to_date.strftime('%d/%m')}",
        "fromDate": from_date.isoformat(),
        "toDate": to_date.isoformat(),
        "status": "ABERTO",
        "generatedAt": datetime.utcnow().isoformat(),
        "createdBy": "system"
    })

    cycle_id = cycle_ref[1].id

    # 2️⃣ Download FAAST
    raw_csv = FaastService.download_faast_csv(
        cycle_id,
        from_date,
        to_date
    )

    # 3️⃣ Processar CSV
    processed = ProcessingService.process_faast_csv(
        raw_csv,
        cycle_id
    )

    # 4️⃣ Upload + Firestore
    for file in processed:
        storage_path = f"cycles/{cycle_id}/{file['fileName']}"

        bucket.upload_cycle_file(
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
            "createdAt": datetime.utcnow().isoformat()
        })

    # 5️⃣ Atualiza ciclo
    db.collection("cycles").document(cycle_id).update({
        "totalFiles": len(processed),
        "status": "ABERTO"
    })
