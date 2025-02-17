import os
import shutil
from pathlib import PurePath

from flask import request
from pdf2image import convert_from_path
from werkzeug.utils import secure_filename

from .config import ALLOWED_EXTENSIONS, UPLOAD_FOLDER


def delete_files_in_folder(folder_path: str | PurePath) -> None:
    for filename in os.listdir(folder_path):
        file_path = os.path.join(folder_path, filename)
        try:
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
        except Exception as e:
            print(f"Failed to delete {file_path}. Reason: {e}")


def convert_pdf_to_images(pdf_path: str | PurePath) -> list[str]:
    images = convert_from_path(pdf_path)
    image_paths = []
    for i, image in enumerate(images):
        image_path = f"{pdf_path}_page_{i}.png"
        image.save(image_path, "PNG")
        image_paths.append(image_path)
    return image_paths


def allowed_file(filename: str) -> bool:
    return (
        "." in filename
        and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS
    )


def handle_files(
    field_names: list[str], errors: list[str] = []
) -> tuple[int, list[str]]:
    file_count = 0
    for field_name in field_names:
        if field_name in request.files:
            file = request.files[field_name]
            if file.filename == "":
                errors.append(f"No file selected for {field_name}")
                continue

            if file and allowed_file(file.filename):
                extension = file.filename.rsplit(".", 1)[1].lower()
                filename = secure_filename(f"{field_name}.{extension}")
                file.save(UPLOAD_FOLDER / filename)
                file_count += 1
            else:
                errors.append(f"File type not allowed for {field_name}")

    return file_count, errors
