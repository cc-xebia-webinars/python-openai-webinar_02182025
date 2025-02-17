# python -m demos.l_image_data

from .app import create_app
from .config import UPLOAD_FOLDER
from .files import delete_files_in_folder


def main() -> None:
    UPLOAD_FOLDER.mkdir(parents=True, exist_ok=True)
    delete_files_in_folder(UPLOAD_FOLDER)
    create_app(UPLOAD_FOLDER).run(port=5000)


if __name__ == "__main__":
    main()
