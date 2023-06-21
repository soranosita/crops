from colorama import Fore

from api import RED, OPS
from args import get_args
from config import Config
from downloader import get_torrent_id, get_torrent_url, get_torrent_filepath, download_torrent
from filesystem import create_folder, get_files, get_filename
from parser import get_torrent_data, get_infohash, get_new_hash, get_source, save_torrent_data
from progress import Progress

def gen_infohash_dict(files):
    infohash_dict = {}
    for file in files:
        torrent_data = get_torrent_data(file)
        infohash = get_infohash(torrent_data)
        infohash_dict[infohash] = torrent_data[b"info"][b"name"].decode("utf8")
    return infohash_dict


def main():
    create_folder(args.folder_out)
    local_torrents = get_files(args.folder_in)
    dest_torrents = get_files(args.folder_out)
    p = Progress(len(local_torrents))
    if args.download:
        p.generated.name = "Downloaded for cross-seeding"

    in_infohash_dict = gen_infohash_dict(local_torrents)
    out_infohash_dict = gen_infohash_dict(dest_torrents)

    for i, torrent_path in enumerate(local_torrents, 1):
        filename = get_filename(torrent_path)
        try:
            torrent_data = get_torrent_data(torrent_path)
        except AssertionError:
            p.error.print("Decoding error.")
            continue
        source = get_source(torrent_data)

        print(f"{i}/{p.total}) {filename}")

        if source == b"OPS" and args.ops_to_red:
            api = red
            new_sources = [b"RED"]
            if args.pth:
                new_sources.append(b"PTH")
        elif source in (b"PTH", b"RED") and args.red_to_ops:
            new_sources = [b"OPS"]
            api = ops
        else:
            p.skipped.print(f"Skipped: source is {source.decode('utf-8')}.")
            continue

        found_infohash_match = False
        for new_source in new_sources:
            hash_ = get_new_hash(torrent_data, new_source)
            if hash_ in in_infohash_dict:
                p.already_exists.print(
                    f"A match was found in the input directory with source {new_source.decode('utf-8')}."
                )
                found_infohash_match = True
                break
            if hash_ in out_infohash_dict:
                p.already_exists.print(
                    f"A match was found in the output directory with source {new_source.decode('utf-8')}."
                )
                found_infohash_match = True
                break

        if found_infohash_match:
            continue

        for i, new_source in enumerate(new_sources, 0):
            hash_ = get_new_hash(torrent_data, new_source)
            torrent_details = api.find_torrent(hash_)
            status = torrent_details["status"]
            new_source = new_source.decode("utf-8")
            known_errors = ("bad hash parameter", "bad parameters")

            if status == "success":
                torrent_filepath = get_torrent_filepath(
                    torrent_details, api.sitename, args.folder_out
                )
                torrent_id = get_torrent_id(torrent_details)

                if args.download:
                    download_torrent(api, torrent_filepath, torrent_id)

                    p.generated.print(
                        f"Found with source {new_source} "
                        f"and downloaded as '{get_filename(torrent_filepath)}'."
                    )
                else:
                    torrent_data[b"announce"] = api.announce_url
                    torrent_data[b"comment"] = get_torrent_url(api.site_url, torrent_id)

                    save_torrent_data(torrent_filepath, torrent_data)

                    p.generated.print(
                        f"Found with source {new_source} "
                        f"and generated as '{get_filename(torrent_filepath)}'."
                    )
                break  # Skip the PTH check if found on RED
            elif torrent_details["error"] in known_errors:
                if not args.pth:
                    p.not_found.print(
                        f"Not found with source {new_source}.",
                        add=False
                    )
                elif args.pth and i == 1:
                    p.not_found.print(
                        f"Not found with sources "
                        f"{', '.join(x.decode('utf-8') for x in new_sources)}.",
                        add=False,
                    )
                p.not_found.increment()
            else:
                p.error.print(
                    f"Unexpected error while using source {new_source}"
                    f"{Fore.LIGHTBLACK_EX}:\n{str(torrent_details)}"
                )

    print(p.report())


if __name__ == "__main__":
    args = get_args()
    config = Config()

    red = RED(config.red_key)
    ops = OPS(config.ops_key)

    main()
