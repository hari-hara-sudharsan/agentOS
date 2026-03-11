import os


DOWNLOAD_DIR = "downloads"


def save_download(download):

    os.makedirs(DOWNLOAD_DIR, exist_ok=True)

    path = f"{DOWNLOAD_DIR}/{download.suggested_filename}"

    download.save_as(path)

    return path
