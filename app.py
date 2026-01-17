from flask import Flask, render_template, redirect, url_for
from config import Config
from api.cycles import cycles_bp
from api.cycle_files import cycle_files_bp
from api.processing import processing_bp
from services.scheduler_service import start_scheduler
from apscheduler.schedulers.background import BackgroundScheduler
from jobs.generate_cycle_job import run_cycle_job
from api.cycle_control import cycle_control_bp
from api.dashboard import dashboard_bp
from api.inventory_adjustments import inventory_adjustments_bp



def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    scheduler = BackgroundScheduler()
    scheduler.add_job(run_cycle_job, "interval", hours=12)
    scheduler.start()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    app.register_blueprint(cycles_bp)
    app.register_blueprint(cycle_files_bp)
    app.register_blueprint(processing_bp)
    app.register_blueprint(cycle_control_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(inventory_adjustments_bp)

    # -----------------------
    # ROTAS PRINCIPAIS (PAGES)
    # -----------------------

    @app.route("/config-test")
    def config_test():
        return {
            "env": app.config["ENV"],
            "cycle_hours": app.config["CYCLE_INTERVAL_HOURS"]
        }

    @app.route("/ajuste-inventario")
    def ajuste_inventario():
        return render_template("ajuste_inventario.html")

    @app.route("/")
    def index():
        return redirect(url_for("dashboard"))

    @app.route("/login")
    def login():
        return render_template("login.html")

    @app.route("/dashboard")
    def dashboard():
        return render_template("dashboard.html")

    @app.route("/cycle-control")
    def cycle_control():
        return render_template("cycle_control.html")

    @app.route("/cycle/<cycle_id>")
    def cycle_detail(cycle_id):
        return render_template("cycle_detail.html", cycle_id=cycle_id)

    # -----------------------
    # HEALTH CHECK
    # -----------------------
    @app.route("/health")
    def health():
        return {"status": "ok", "system": "Cycle Control"}, 200

    return app


if __name__ == "__main__":
    app = create_app()
    start_scheduler()
    app.run(debug=True)

