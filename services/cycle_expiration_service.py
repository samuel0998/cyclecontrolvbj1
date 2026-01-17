from datetime import datetime
from services.firebase_service import db


class CycleExpirationService:

    @staticmethod
    def expire_cycles():
        now = datetime.utcnow()
        now_iso = now.isoformat()

        cycles = (
            db.collection("cycles")
            .where("status", "in", ["ABERTO", "EM_COLETA"])
            .stream()
        )

        expired_cycles = 0

        for cycle in cycles:
            data = cycle.to_dict()
            expires_at = data.get("expiresAt")

            if not expires_at:
                continue

            expires_at_dt = datetime.fromisoformat(expires_at)

            if expires_at_dt <= now:
                # 🔁 Marca ciclo como LOST
                db.collection("cycles").document(cycle.id).update({
                    "status": "LOST",
                    "lostAt": now_iso
                })

                # 🔁 Marca arquivos pendentes como LOST
                files = (
                    db.collection("cycle_files")
                    .where("cycleId", "==", cycle.id)
                    .where("status", "in", ["PENDENTE", "EM_CONTAGEM"])
                    .stream()
                )

                for f in files:
                    db.collection("cycle_files").document(f.id).update({
                        "status": "LOST"
                    })

                expired_cycles += 1
                print(f"⏰ Cycle LOST: {cycle.id}")

        if expired_cycles:
            print(f"🔥 Cycles expirados: {expired_cycles}")
