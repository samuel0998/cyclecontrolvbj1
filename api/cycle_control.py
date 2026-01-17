from flask import Blueprint, jsonify
from datetime import datetime, timedelta

from services.faast_service import FaastService
from services.processing_service import ProcessingService
from services.storage_service import StorageService
from services.firebase_service import db


cycle_control_bp = Blueprint(
    "cycle_control",
    __name__,
    url_prefix="/api/cycle-control"
)


@cycle_control_bp.route("/start", methods=["POST"])
def start_cycle_control():
    """
    Fluxo completo:
    1. Cria ciclo (com expiração)
    2. Abre FAAST e aguarda download
    3. Processa CSV
    4. Gera CSVs por AA
    5. Upload Firebase Storage
    6. Registra arquivos no Firestore
    """

    # =========================
    # 1️⃣ CRIAR CICLO
    # =========================
    now = datetime.utcnow()
    expires_at = now + timedelta(hours=12)

    cycle_ref = db.collection("cycles").add({
        "status": "EM_COLETA",
        "createdAt": now.isoformat(),
        "expiresAt": expires_at.isoformat(),
        "createdBy": "manual"
    })

    cycle_id = cycle_ref[1].id
    print(f"🔁 Ciclo criado: {cycle_id}")

    # =========================
    # 2️⃣ FAAST (DOWNLOAD)
    # =========================
    raw_csv_path = FaastService.download_faast_csv(cycle_id)

    if not raw_csv_path or not raw_csv_path.endswith(".csv"):
        return jsonify({
            "error": "CSV FAAST não localizado"
        }), 400

    print(f"📥 CSV FAAST: {raw_csv_path}")

    # =========================
    # 3️⃣ PROCESSAR CSV
    # =========================
    processed_files = ProcessingService.process_faast_csv(
        raw_csv_path,
        cycle_id
    )

    if not processed_files:
        return jsonify({
            "error": "CSV processado, mas nenhum arquivo válido foi gerado"
        }), 400

    # =========================
    # 4️⃣ UPLOAD + FIRESTORE
    # =========================
    uploaded = 0

    for file in processed_files:
        try:
            storage_path = f"cycles/{cycle_id}/{file['fileName']}"

            # ☁️ Upload Storage
            StorageService.upload_cycle_file(
                local_path=file["localPath"],
                storage_path=storage_path
            )

            # 🧾 Firestore
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

            uploaded += 1
            print(f"☁️ Upload OK: {file['fileName']}")

        except Exception as e:
            print(f"❌ Erro upload {file['fileName']}: {e}")

    # =========================
    # 5️⃣ FINALIZAR CICLO
    # =========================
    db.collection("cycles").document(cycle_id).update({
        "status": "ABERTO",
        "totalFiles": uploaded
    })

    print(f"✅ Ciclo {cycle_id} finalizado ({uploaded} arquivos)")

    return jsonify({
        "message": "Cycle criado com sucesso!",
        "cycleId": cycle_id,
        "files": uploaded
    }), 200
