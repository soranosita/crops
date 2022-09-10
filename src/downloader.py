from html import unescape
import os


def get_torrent_id(result):
    return result["response"]["torrent"]["id"]


def get_torrent_filepath(torrent_details, source, folder_out):
    filename = (
        f'{unescape(torrent_details["response"]["torrent"]["filePath"])} '
        f'[{source}].torrent'
    )
    return os.path.join(folder_out, filename)


def download_torrent(api, torrent_details, folder_out):
    torrent_id = get_torrent_id(torrent_details)
    torrent_filepath = get_torrent_filepath(torrent_details, api.sitename, folder_out)

    if os.path.isfile(torrent_filepath):
        return None

    with open(torrent_filepath, "wb") as f:
        r = api.download_torrent(torrent_id)
        f.write(r.content)
    return torrent_filepath
