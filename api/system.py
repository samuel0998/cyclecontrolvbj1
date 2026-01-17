from flask import Blueprint, jsonify
from services.cycle_expiration_service import CycleExpirationService

system_bp = Blueprint("system", __name__, url_prefix="/api/system")

@system_bp.route("/expire-cycles", methods=["POST"])
def expire_cycles():
    count = CycleExpirationService.expire_cycles()
    return jsonify({
        "expiredCycles": count
    })
