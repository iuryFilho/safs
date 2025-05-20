from flask import Flask, render_template
import argparse
from routes import metrics

app = Flask(__name__)
app.secret_key = "supersecretkey"
app.register_blueprint(metrics, url_prefix="/metrics")


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

    app.run(host="127.0.0.1", port=args.port, debug=args.no_debug)


if __name__ == "__main__":
    main()
