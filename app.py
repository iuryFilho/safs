from flask import Flask, render_template
import argparse
from routes import metrics, debug_output

app = Flask(__name__)
app.secret_key = "supersecretkey"


@app.route("/")
def index():
    return render_template("index.jinja")


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
    global debug_output
    debug_output = args.no_debug
    app.register_blueprint(metrics, url_prefix="/metrics", debug_output=debug_output)
    app.run(host="127.0.0.1", port=args.port, debug=args.no_debug)


if __name__ == "__main__":
    main()
