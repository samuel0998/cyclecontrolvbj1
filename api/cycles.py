from flask import Blueprint, jsonify
from services.firebase_service import db

cycles_bp = Blueprint(
    "cycles",
    __name__,
    url_prefix="/api/cycles"
)


@cycles_bp.route("/active", methods=["GET"])
def get_active_cycle():
    docs = (
        db.collection("cycles")
        .where("status", "==", "ABERTO")
        .limit(1)
        .stream()
    )

    for doc in docs:
        data = doc.to_dict()
        data["id"] = doc.id
        return jsonify(data), 200

    return jsonify(None), 200

