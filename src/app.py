from flask import Blueprint, Flask
import argparse
from routes import (
    config_route as cr,
    generation_route as gr,
    home_route as hr,
    tutorial_route as tr,
)


def create_app(*, blueprints: dict[str, Blueprint] = None):
    app = Flask(__name__)
    app.secret_key = "supersecretkey"
    app.config["TEMPLATES_AUTO_RELOAD"] = True

    if isinstance(blueprints, dict):
        for url, blueprint in blueprints.items():
            if (
                isinstance(url, str)
                and url.startswith("/")
                and isinstance(blueprint, Blueprint)
            ):
                app.register_blueprint(blueprint, url_prefix=url)

    return app


def main():
    parser = argparse.ArgumentParser(description="Run the Flask app.")
    parser.add_argument(
        "--port", type=int, default=5000, help="Port to run the server on"
    )
    parser.add_argument(
        "--no-debug", action="store_false", help="Disable debug mode for the server"
    )
    args = parser.parse_args()
    blueprints = {
        "/": hr.blueprint,
        "/config": cr.blueprint,
        "/generation": gr.blueprint,
        "/tutorial": tr.blueprint,
    }
    app = create_app(blueprints=blueprints)
    app.run(
        host="127.0.0.1",
        port=args.port,
        debug=args.no_debug,
    )


if __name__ == "__main__":
    main()
