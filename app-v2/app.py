import os
import socket
import logging
from flask import Flask, jsonify

APP_VERSION = "v2"
APP_NAME = "zero-downtime-demo"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s %(message)s",
)
logger = logging.getLogger(APP_NAME)

app = Flask(__name__)


@app.route("/")
def index():
    logger.info("Serving index page from version %s", APP_VERSION)
    return (
        f"<html><body>"
        f"<h1>Version 2 - New Release</h1>"
        f"<p>Application: {APP_NAME}</p>"
        f"<p>Version: {APP_VERSION}</p>"
        f"<p>Served by container: {socket.gethostname()}</p>"
        f"</body></html>"
    )


@app.route("/health")
def health():
    payload = {
        "status": "healthy",
        "version": APP_VERSION,
        "app": APP_NAME,
        "hostname": socket.gethostname(),
    }
    logger.info("Health check hit: %s", payload)
        return jsonify(payload), 200


@app.route("/version")
def version():
    return jsonify({"version": APP_VERSION, "app": APP_NAME}), 200


@app.errorhandler(404)
def not_found(error):
    logger.warning("404 for request: %s", error)
    return jsonify({"error": "not found", "version": APP_VERSION}), 404


@app.errorhandler(500)
def server_error(error):
    logger.error("500 for request: %s", error)
    return jsonify({"error": "internal server error", "version": APP_VERSION}), 500


if __name__ == "__main__":
    port = int(os.environ.get("PORT", "5000"))
    logger.info("Starting %s %s on port %s (dev server)", APP_NAME, APP_VERSION, port)
    app.run(host="0.0.0.0", port=port)
