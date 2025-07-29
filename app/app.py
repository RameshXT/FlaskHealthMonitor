from flask import Flask
from routes.health import health_bp
from routes.metrics import metrics_bp
from routes.thresholds import thresholds_bp
from routes.alerts import alerts_bp
from background.collector import start_metric_collector
from models.db import initialize_db

def create_app():
    app = Flask(__name__)

    # Initialize DB
    initialize_db()

    # Start background thread
    start_metric_collector()

    # Register Blueprints
    app.register_blueprint(health_bp)
    app.register_blueprint(metrics_bp)
    app.register_blueprint(thresholds_bp)
    app.register_blueprint(alerts_bp)

    return app

if __name__ == "__main__":
    app = create_app()
    app.run(host="0.0.0.0", port=5000)
