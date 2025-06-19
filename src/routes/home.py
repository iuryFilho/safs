from flask import (
    Blueprint,
    jsonify,
    render_template,
    session,
)

blueprint = Blueprint("home", __name__)


@blueprint.route("/")
def index():
    return render_template("home.jinja")


@blueprint.route("/clear-session", methods=["POST"])
def clear_session():
    """Clear the session data."""
    try:
        session.clear()
        return jsonify({"message": "Session cleared successfully."}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
