from datetime import datetime
from services.firebase_service import db




class CycleExpirationService:

    @staticmethod
    def expire_cycles():
        now = datetime.utcnow().isoformat()

        cycles = (
            db.collection("cycles")
            .where("status", "in", ["ABERTO", "EM_COLETA"])
            .stream()
        )

        expired = 0

        for cycle in cycles:
            data = cycle.to_dict()

            if data.get("expiresAt") and data["expiresAt"] < now:
                # Marca ciclo como LOST
                db.collection("cycles").document(cycle.id).update({
                    "status": "LOST",
                    "lostAt": now
                })

                # Marca arquivos pendentes como LOST
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

                expired += 1

        return expired
