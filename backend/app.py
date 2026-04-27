"""
ATM Network Security Audit System - Main Flask Application
"""
from flask import Flask
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from dotenv import load_dotenv
import os

load_dotenv()

app = Flask(__name__)
app.config["JWT_SECRET_KEY"] = os.getenv("JWT_SECRET_KEY", "fallback_secret")
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = 3600  # 1 hour

CORS(app, resources={r"/api/*": {"origins": "http://localhost:3000"}})
jwt = JWTManager(app)

# Register blueprints
from modules.auth import auth_bp
from modules.transactions import transactions_bp
from modules.security_scan import security_bp
from modules.risk_analysis import risk_bp
from modules.anomaly import anomaly_bp
from modules.reports import reports_bp

app.register_blueprint(auth_bp, url_prefix="/api/auth")
app.register_blueprint(transactions_bp, url_prefix="/api/transactions")
app.register_blueprint(security_bp, url_prefix="/api/security")
app.register_blueprint(risk_bp, url_prefix="/api/risk")
app.register_blueprint(anomaly_bp, url_prefix="/api/anomaly")
app.register_blueprint(reports_bp, url_prefix="/api/reports")

@app.route("/api/health")
def health():
    return {"status": "ok", "message": "ATM Security System running"}

if __name__ == "__main__":
    port = int(os.getenv("FLASK_PORT", 5000))
    app.run(debug=True, port=port)
