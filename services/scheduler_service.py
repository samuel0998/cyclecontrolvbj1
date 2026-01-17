from apscheduler.schedulers.background import BackgroundScheduler
from services.cycle_expiration_service import CycleExpirationService

scheduler = BackgroundScheduler()


def start_scheduler():
    scheduler.add_job(
        func=CycleExpirationService.expire_cycles,
        trigger="interval",
        minutes=5,   # ⏰ ajuste aqui se quiser
        id="cycle_expiration_job",
        replace_existing=True
    )

    scheduler.start()
    print("⏱️ Scheduler iniciado (Cycle Lost ativo)")
