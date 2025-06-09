from flask import Flask, jsonify, render_template, session
import argparse
from routes import config as cr, generation as gr

app = Flask(__name__)
app.secret_key = "supersecretkey"


@app.route("/")
def index():
    return render_template("home.jinja")


@app.route("/clear-session", methods=["POST"])
def clear_session():
    """Clear the session data."""
    try:
        session.clear()
        return jsonify({"message": "Session cleared successfully."}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


def main():
    parser = argparse.ArgumentParser(description="Run the Flask app.")
    parser.add_argument(
        "--port", type=int, default=5000, help="Port to run the server on"
    )
    parser.add_argument(
        "--no-debug", action="store_false", help="Disable debug mode for the server"
    )
    args = parser.parse_args()
    app.config["TEMPLATES_AUTO_RELOAD"] = True
    app.register_blueprint(
        cr.blueprint, url_prefix="/config", debug_output=args.no_debug
    )
    app.register_blueprint(
        gr.blueprint, url_prefix="/generation", debug_output=args.no_debug
    )
    app.run(host="127.0.0.1", port=args.port, debug=args.no_debug)


if __name__ == "__main__":
    main()
