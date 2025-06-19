from flask import (
    Blueprint,
    render_template,
)

blueprint = Blueprint("tutorial", __name__)


@blueprint.route("/")
def index():
    return render_template("tutorial.jinja")
