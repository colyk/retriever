import re

import requests


def is_exist(url: str) -> bool:
    return requests.head(url, allow_redirects=True).ok


def download_file(url: str, filename: str = None, show_status: bool = True):
    # TODO add downloading status bar
    res = requests.get(url, allow_redirects=True, stream=True)
    filename = filename or __get_filename(
        res.headers.get('Content-Disposition'), res.url
    )
    if not __is_content_type_valid(res.headers.get('Content-Type')):
        raise RuntimeError('Bad filename')
    if not res.ok:
        raise RuntimeError('Requests error')

    if show_status:
        total_length = int(res.headers.get('Content-Length'))
        print('File size is:', humanize_bytes(total_length))
    f = open(filename, 'wb')
    for chunk in res.iter_content(chunk_size=4096):
        if chunk:
            f.write(chunk)


def __is_content_type_valid(content_type):
    ct = content_type.lower()
    if 'text' in ct:
        return False
    if 'html' in ct:
        return False
    return True


def __get_filename(cd, url):
    if cd is None:
        return url.split('/')[-1]
    filename = re.findall('filename=(.+)', cd)
    if not filename:
        raise ValueError('Provide filename')
    return filename[0]


def humanize_bytes(size: int, precision: int = 2, as_obj=False):
    assert isinstance(size, int)
    power = 1024
    n = 0
    units = {
        0: "B", 1: "kB",
        2: "MB", 3: "GB",
        4: "TB", 5: "PB",
        6: "EB"
    }
    while size >= power:
        size /= power
        n += 1
    size = round(size, precision)
    if as_obj:
        return size, units[n]
    return str(size) + units[n]
