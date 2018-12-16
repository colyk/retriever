import re

import requests


def is_exist(url: str) -> bool:
    return requests.head(url, allow_redirects=True).ok


def download_file(url: str, filename: str = None, show_status:bool=False):
    # TODO add downloading status bar 
    res = requests.get(url, allow_redirects=True, stream=True)
    filename = filename or __get_filename(res)
    total_length = res.headers.get('Content-Length')
    if not __is_content_type_valide(filename, res.headers.get("Content-Type")):
        raise RuntimeError("Bad filename")
    if not res.ok:
        raise RuntimeError("Requests error")

    downloaded_file = open(filename, "wb")
    for chunk in res.iter_content(chunk_size=4096):
        if chunk:
            downloaded_file.write(chunk)


def __is_content_type_valide(filename, content_type):
    file_extention = filename.split(".")[-1]
    ct = content_type.lower()
    if "text" in ct.lower():
        return False
    if "html" in ct.lower():
        return False
    return file_extention in ct


def __get_filename(response):
    if response.headers.get("Content-Disposition") is None:
        return response.url.split("/")[-1]
    filename = re.findall("filename=(.+)", cd)
    if not filename:
        return None
    return filename[0]
