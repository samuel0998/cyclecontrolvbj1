from flask import Blueprint, request, jsonify
from datetime import datetime
from services.firebase_service import db
from services.storage_service import StorageService

cycle_files_bp = Blueprint(
    "cycle_files",
    __name__,
    url_prefix="/api/cycle-files"
)

# =====================================================
# 🔹 LISTAR CONTAGENS DO CICLO
# =====================================================
@cycle_files_bp.route("/<cycle_id>", methods=["GET"])
def list_cycle_files(cycle_id):

    docs = (
        db.collection("cycle_files")
        .where("cycleId", "==", cycle_id)
        .stream()
    )

    files = []
    for doc in docs:
        data = doc.to_dict()
        data["id"] = doc.id
        files.append(data)

    return jsonify(files), 200


# =====================================================
# 🔹 CRIAR CONTAGEM (APÓS PROCESSAMENTO DO CSV)
# =====================================================
@cycle_files_bp.route("", methods=["POST"])
def create_cycle_file():
    data = request.json

    file_doc = {
        "cycleId": data["cycleId"],

        "aaLogin": data["aaLogin"],

        "fileName": data["fileName"],
        "storagePath": data["storagePath"],

        "totalAddresses": data["totalAddresses"],
        "totalSkus": data["totalSkus"],

        # 🔹 CONTROLE
        "status": "PENDENTE",
        "countLevel": 1,               # 1 = First | 2 = Second

        # 🔹 DADOS DE CONTAGEM
        "faastCountId": None,
        "errorsFound": None,

        # 🔹 CONTADORES
        "firstCounter": None,
        "secondCounter": None,

        # 🔹 RELAÇÕES
        "parentCountId": None,

        # 🔹 TIMESTAMPS
        "createdAt": datetime.utcnow().isoformat(),
        "finishedAt": None
    }

    ref = db.collection("cycle_files").add(file_doc)

    return jsonify({
        "message": "Contagem criada com sucesso",
        "fileId": ref[1].id
    }), 201


# =====================================================
# 🔹 ATRIBUIR CONTADOR + ID FAAST
# =====================================================
@cycle_files_bp.route("/<file_id>/assign", methods=["POST"])
def assign_counter(file_id):
    data = request.json

    counter = data.get("counterUid")
    faast_id = data.get("faastCountId")

    if not counter or not faast_id:
        return jsonify({
            "error": "Contador e ID FAAST são obrigatórios"
        }), 400

    ref = db.collection("cycle_files").document(file_id)
    doc = ref.get()

    if not doc.exists:
        return jsonify({"error": "Contagem não encontrada"}), 404

    d = doc.to_dict()

    # 🔒 BACKWARD COMPATIBILITY
    count_level = d.get("countLevel", 1)

    if d.get("status") not in ["PENDENTE", "SECOND_COUNT"]:
        return jsonify({
            "error": "Contagem não pode ser atribuída neste status"
        }), 400

    update = {
        "faastCountId": faast_id,
        "status": "EM_CONTAGEM"
    }

    # ======================
    # FIRST COUNT
    # ======================
    if count_level == 1:
        update["firstCounter"] = counter

        # 🔧 GARANTE PADRÃO
        update["countLevel"] = 1

    # ======================
    # SECOND COUNT
    # ======================
    else:
        first_counter = d.get("firstCounter")

        if counter == first_counter:
            return jsonify({
                "error": "O segundo contador não pode ser o mesmo da primeira contagem"
            }), 400

        update["secondCounter"] = counter
        update["countLevel"] = 2

    ref.update(update)

    return jsonify({"message": "Contador atribuído com sucesso"}), 200



# =====================================================
# 🔹 FINALIZAR CONTAGEM
# =====================================================
@cycle_files_bp.route("/<file_id>/finish", methods=["POST"])
def finish_count(file_id):
    data = request.json
    errors = int(data.get("errorsFound", -1))

    if errors < 0:
        return jsonify({"error": "Número de erros inválido"}), 400

    ref = db.collection("cycle_files").document(file_id)
    doc = ref.get()

    if not doc.exists:
        return jsonify({"error": "Contagem não encontrada"}), 404

    d = doc.to_dict()
    count_level = d.get("countLevel", 1)

    now = datetime.utcnow().isoformat()

    # =========================
    # PRIMEIRA CONTAGEM
    # =========================
    if count_level == 1:

        # 🔹 SEM ERROS → FECHA
        if errors == 0:
            ref.update({
                "firstErrors": 0,
                "status": "FECHADO",
                "finishedAt": now
            })
            return jsonify({"message": "Contagem finalizada sem erros"}), 200

        # 🔁 COM ERROS → SEGUNDA CONTAGEM
        ref.update({
            "firstErrors": errors,
            "status": "SECOND_COUNT",
            "countLevel": 2
        })

        return jsonify({
            "message": "Second Count liberada",
            "next": "SECOND_COUNT"
        }), 200

    # =========================
    # SEGUNDA CONTAGEM
    # =========================
    if count_level == 2:

        ref.update({
            "secondErrors": errors,
            "status": "FECHADO",
            "finishedAt": now
        })

        if errors > 0:
            db.collection("inventory_adjustments").add({
                "cycleId": d["cycleId"],
                "originCountId": file_id,

                "firstCounter": d.get("firstCounter"),
                "secondCounter": d.get("secondCounter"),

                "firstErrors": d.get("firstErrors"),
                "secondErrors": errors,

                "status": "PENDENTE",
                "createdAt": now
            })

        return jsonify({
            "message": "Contagem finalizada (segunda)",
            "adjustment": errors > 0
        }), 200


# =====================================================
# 🔹 DELETAR CONTAGEM
# =====================================================
@cycle_files_bp.route("/<file_id>", methods=["DELETE"])
def delete_cycle_file(file_id):

    db.collection("cycle_files").document(file_id).delete()

    return jsonify({"message": "Contagem deletada"}), 200


# =====================================================
# 🔹 DOWNLOAD CSV (FIREBASE STORAGE)
# =====================================================
@cycle_files_bp.route("/<file_id>/download", methods=["GET"])
def download_cycle_file(file_id):

    doc = db.collection("cycle_files").document(file_id).get()

    if not doc.exists:
        return jsonify({"error": "Arquivo não encontrado"}), 404

    data = doc.to_dict()
    signed_url = StorageService.generate_signed_url(data["storagePath"])

    return jsonify({"url": signed_url}), 200
