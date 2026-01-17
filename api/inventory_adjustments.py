from flask import Blueprint, jsonify
from datetime import datetime
from services.firebase_service import db

inventory_adjustments_bp = Blueprint(
    "inventory_adjustments",
    __name__,
    url_prefix="/api/inventory-adjustments"
)


# 🔹 LISTAR AJUSTES (PENDENTES E FINALIZADOS)
@inventory_adjustments_bp.route("", methods=["GET"])
def list_adjustments():

    docs = (
        db.collection("inventory_adjustments")
        .order_by("createdAt", direction="DESCENDING")
        .stream()
    )

    adjustments = []

    for doc in docs:
        data = doc.to_dict()
        data["id"] = doc.id
        adjustments.append(data)

    return jsonify(adjustments), 200


# 🔹 FINALIZAR AJUSTE
@inventory_adjustments_bp.route("/<adjustment_id>/finish", methods=["POST"])
def finish_adjustment(adjustment_id):

    ref = db.collection("inventory_adjustments").document(adjustment_id)
    doc = ref.get()

    if not doc.exists:
        return jsonify({"error": "Ajuste não encontrado"}), 404

    ref.update({
        "status": "FINALIZADO",
        "finishedAt": datetime.utcnow().isoformat()
    })

    return jsonify({"message": "Ajuste finalizado com sucesso"}), 200
