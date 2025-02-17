from pathlib import PurePath

from flask import (
    Flask,
    render_template,
    request,
)
from werkzeug.wrappers import Response

from .bills import get_bill_details
from .files import delete_files_in_folder, handle_files


def create_app(upload_folder: PurePath) -> Flask:
    app = Flask(__name__)
    app.config["UPLOAD_FOLDER"] = upload_folder

    @app.route("/", methods=["GET", "POST"])
    def upload_file() -> Response | str:
        if request.method == "POST":
            errors: list[str] = []
            file_count, errors = handle_files(["invoice", "receipt"], errors)

            if file_count == 0:
                errors.append("No invoice or receipt")
                return render_template("index.html", errors=errors)
            else:
                bill_details: list[str] = get_bill_details(upload_folder)
                delete_files_in_folder(upload_folder)
                return render_template("index.html", bill_details=bill_details)

        return render_template("index.html")

    return app
