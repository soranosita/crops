from hashlib import sha1

import bencoder


def get_source(torrent_data):
    try:
        return torrent_data[b"info"][b"source"]
    except KeyError:
        return b"empty"


def get_new_hash(torrent_data, new_source):
    torrent_data[b"info"][b"source"] = new_source
    hash = sha1(bencoder.bencode(torrent_data[b"info"])).hexdigest().upper()

    return hash


def get_torrent_data(filename):
    with open(filename, "rb") as f:
        data = bencoder.bdecode(f.read())

    return data


def save_torrent_data(filename, torrent_data):
    with open(filename, "wb") as f:
        f.write(bencoder.bencode(torrent_data))
