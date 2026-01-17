from flask import Blueprint, request, jsonify
from datetime import datetime
from services.firebase_service import db

cycle_files_bp = Blueprint(
    "cycle_files",
    __name__,
    url_prefix="/api/cycle-files"
)


# 🔹 LISTAR ARQUIVOS DO CICLO
@cycle_files_bp.route("/<cycle_id>", methods=["GET"])
def list_cycle_files(cycle_id):

    docs = db.collection("cycle_files") \
        .where("cycleId", "==", cycle_id) \
        .stream()

    files = []
    for doc in docs:
        data = doc.to_dict()
        data["id"] = doc.id
        files.append(data)

    return jsonify(files), 200


# 🔹 CRIAR ARQUIVO (APÓS PROCESSAR CSV)
@cycle_files_bp.route("", methods=["POST"])
def create_cycle_file():
    data = request.json

    file_doc = {
        "cycleId": data["cycleId"],

        "aaLogin": data["aaLogin"],
        "aaName": data.get("aaName"),

        "fileName": data["fileName"],
        "storagePath": data["storagePath"],

        "totalAddresses": data["totalAddresses"],
        "totalSkus": data["totalSkus"],

        "status": "PENDENTE",

        "assignedCounter": None,
        "assignedAt": None,

        "errorsFound": None,
        "finishedAt": None
    }

    ref = db.collection("cycle_files").add(file_doc)

    return jsonify({
        "message": "Arquivo de ciclo criado",
        "fileId": ref[1].id
    }), 201


# 🔹 ATRIBUIR CONTADOR
@cycle_files_bp.route("/<file_id>/assign", methods=["POST"])
def assign_counter(file_id):
    data = request.json

    db.collection("cycle_files").document(file_id).update({
        "assignedCounter": data["counterUid"],
        "assignedAt": datetime.utcnow().isoformat(),
        "status": "EM_CONTAGEM"
    })

    return jsonify({"message": "Contador atribuído"}), 200


# 🔹 FINALIZAR CONTAGEM
@cycle_files_bp.route("/<file_id>/finish", methods=["POST"])
def finish_count(file_id):
    data = request.json

    db.collection("cycle_files").document(file_id).update({
        "errorsFound": data["errorsFound"],
        "finishedAt": datetime.utcnow().isoformat(),
        "status": "FECHADO"
    })

    return jsonify({"message": "Contagem finalizada"}), 200


# 🔹 DELETAR ARQUIVO
@cycle_files_bp.route("/<file_id>", methods=["DELETE"])
def delete_cycle_file(file_id):

    db.collection("cycle_files").document(file_id).delete()

    return jsonify({"message": "Arquivo deletado"}), 200
