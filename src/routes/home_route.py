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
