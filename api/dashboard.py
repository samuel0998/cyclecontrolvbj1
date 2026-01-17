from flask import Blueprint, jsonify
from services.firebase_service import db
from datetime import datetime, timedelta

dashboard_bp = Blueprint(
    "dashboard",
    __name__,
    url_prefix="/api/dashboard"
)


@dashboard_bp.route("/summary", methods=["GET"])
def dashboard_summary():

    # 🔁 Ciclos
    cycles = list(db.collection("cycles").stream())
    total_cycles = len(cycles)

    # ❌ Cycle Lost
    cycle_lost = len([
        c for c in cycles
        if c.to_dict().get("status") == "EXPIRED"
    ])

    # 🔍 Ciclo ativo
    active_cycle = None
    for c in cycles:
        if c.to_dict().get("status") == "ABERTO":
            active_cycle = c
            break

    aa_count = 0
    total_items = 0

    if active_cycle:
        cycle_id = active_cycle.id
        files = (
            db.collection("cycle_files")
            .where("cycleId", "==", cycle_id)
            .stream()
        )

        aa_logins = set()

        for f in files:
            d = f.to_dict()
            aa_logins.add(d["aaLogin"])
            total_items += d.get("totalAddresses", 0)

        aa_count = len(aa_logins)

    return jsonify({
        "currentShift": "--",
        "aaAudited": aa_count,
        "itemsProcessed": total_items,
        "totalCycles": total_cycles,
        "cycleLost": cycle_lost
    })

@dashboard_bp.route("/charts", methods=["GET"])
def dashboard_charts():
    files = db.collection("cycle_files").stream()

    aa_counter = {}
    status_counter = {
        "PENDENTE": 0,
        "EM_CONTAGEM": 0,
        "FECHADO": 0,
        "LOST": 0
    }

    for doc in files:
        d = doc.to_dict()

        # 🔒 PROTEÇÃO TOTAL
        aa = d.get("aaLogin")
        total = d.get("totalSkus", 0)
        status = d.get("status")

        # ===== PRODUTIVIDADE POR AA =====
        if aa:
            aa_counter[aa] = aa_counter.get(aa, 0) + total

        # ===== STATUS DAS CONTAGENS =====
        if status in status_counter:
            status_counter[status] += 1

    return jsonify({
        "aaLabels": list(aa_counter.keys()),
        "aaValues": list(aa_counter.values()),
        "statusLabels": list(status_counter.keys()),
        "statusValues": list(status_counter.values())
    }), 200


@dashboard_bp.route("/cycles", methods=["GET"])
def dashboard_cycles():

    cycles = (
        db.collection("cycles")
        .order_by("createdAt", direction="DESCENDING")
        .limit(5)
        .stream()
    )

    result = []

    for c in cycles:
        d = c.to_dict()
        created = datetime.fromisoformat(d["createdAt"])
        expires = created + timedelta(hours=12)

        result.append({
            "id": c.id,
            "period": f"{created.strftime('%d/%m %H:%M')} → {expires.strftime('%H:%M')}",
            "status": d["status"],
            "timeLost": max(0, int((expires - datetime.utcnow()).total_seconds() / 60))
        })

    return jsonify(result)
