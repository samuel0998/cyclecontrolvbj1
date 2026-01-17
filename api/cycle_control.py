from flask import Blueprint, jsonify
from datetime import datetime

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
    Fluxo:
    1. Cria um novo ciclo
    2. Abre FAAST (download manual)
    3. Processa CSV FAAST
    4. Gera CSVs por AA
    5. Upload Firebase Storage
    6. Registra no Firestore
    """

    # =========================
    # 1️⃣ CRIAR CICLO
    # =========================
    cycle_ref = db.collection("cycles").add({
        "status": "EM_COLETA",
        "createdAt": datetime.utcnow().isoformat(),
        "createdBy": "manual"
    })

    cycle_id = cycle_ref[1].id
    print(f"🔁 Novo ciclo criado: {cycle_id}")

    # =========================
    # 2️⃣ FAAST (DOWNLOAD MANUAL)
    # =========================
    raw_csv_path = FaastService.download_faast_csv(cycle_id)

    if not raw_csv_path:
        return jsonify({"error": "CSV FAAST não encontrado"}), 400

    print(f"📥 CSV FAAST localizado: {raw_csv_path}")

    # =========================
    # 3️⃣ PROCESSAR CSV
    # =========================
    processed_files = ProcessingService.process_faast_csv(
        raw_csv_path,
        cycle_id
    )

    if not processed_files:
        return jsonify({"error": "Nenhum arquivo gerado no processamento"}), 400

    print("📂 Arquivos processados:")
    for f in processed_files:
        print(" -", f["fileName"])

    # =========================
    # 4️⃣ UPLOAD + FIRESTORE
    # =========================
    uploaded_count = 0

    for file in processed_files:
        try:
            storage_path = f"cycles/{cycle_id}/{file['fileName']}"

            # 🔼 UPLOAD STORAGE
            StorageService.upload_cycle_file(
                local_path=file["localPath"],
                storage_path=storage_path
            )

            # 🧾 FIRESTORE
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

            uploaded_count += 1
            print(f"☁️ Upload OK: {file['fileName']}")

        except Exception as e:
            print(f"❌ Erro ao subir {file['fileName']}: {str(e)}")

    # =========================
    # 5️⃣ FINALIZAR CICLO
    # =========================
    db.collection("cycles").document(cycle_id).update({
        "status": "ABERTO",
        "totalFiles": uploaded_count
    })

    print(f"✅ Ciclo {cycle_id} finalizado com {uploaded_count} arquivos")

    return jsonify({
        "message": "Cycle Control gerado com sucesso",
        "cycleId": cycle_id,
        "files": uploaded_count
    }), 200
