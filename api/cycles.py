from flask import Blueprint, jsonify, request
from datetime import datetime
import os

from services.firebase_service import db
from utils.time_utils import calculate_time_left


cycles_bp = Blueprint(
    "cycles",
    __name__,
    url_prefix="/api/cycles"
)

ADMIN_PASSWORD = os.getenv("ADMIN_DELETE_PASSWORD", "#vbj1")

@cycles_bp.route("/recent", methods=["GET"])
def get_recent_cycles():
    docs = (
        db.collection("cycles")
        .order_by("createdAt", direction="DESCENDING")
        .limit(5)
        .stream()
    )

    cycles = []

    for doc in docs:
        data = doc.to_dict()
        data["id"] = doc.id

        # ⏳ TEMPO RESTANTE
        if data.get("expiresAt"):
            data["timeLeft"] = calculate_time_left(data["expiresAt"])
        else:
            data["timeLeft"] = None

        cycles.append(data)

    return jsonify(cycles), 200


# ======================================================
# 🔹 CICLO ATIVO (com timeLeft)
# ======================================================
@cycles_bp.route("/active", methods=["GET"])
def get_active_cycle():
    docs = db.collection("cycles").stream()

    for doc in docs:
        data = doc.to_dict()

        if data.get("status") == "ABERTO":
            data["id"] = doc.id
            return jsonify(data), 200

    return jsonify(None), 200



# ======================================================
# 🔹 LISTAR CICLOS (para dashboard)
# ======================================================
@cycles_bp.route("", methods=["GET"])
def list_cycles():
    docs = (
        db.collection("cycles")
        .order_by("createdAt", direction="DESCENDING")
        .limit(20)
        .stream()
    )

    cycles = []

    for doc in docs:
        data = doc.to_dict()
        data["id"] = doc.id

        data["timeLeft"] = (
            calculate_time_left(data["expiresAt"])
            if data.get("expiresAt")
            else 0
        )

        cycles.append(data)

    return jsonify(cycles), 200


# ======================================================
# 🔹 DELETAR CICLO (ADMIN)
# ======================================================
@cycles_bp.route("/<cycle_id>/delete", methods=["POST"])
def delete_cycle(cycle_id):
    data = request.json or {}
    password = data.get("password")

    if password != ADMIN_PASSWORD:
        return jsonify({"error": "Senha inválida"}), 403

    # 🔹 Deletar arquivos do ciclo
    files = (
        db.collection("cycle_files")
        .where("cycleId", "==", cycle_id)
        .stream()
    )

    deleted_files = 0

    for f in files:
        db.collection("cycle_files").document(f.id).delete()
        deleted_files += 1

    # 🔹 Deletar ciclo
    db.collection("cycles").document(cycle_id).delete()

    return jsonify({
        "message": "Ciclo deletado com sucesso",
        "filesDeleted": deleted_files
    }), 200
