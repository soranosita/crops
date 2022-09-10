from time import time

from colorama import Fore

from api import RED, OPS
from args import get_args
from config import Config
from downloader import download_torrent
from filesystem import create_folder, get_files, get_filename
from parser import get_torrent_data, get_new_hash, get_source


def main():
    start_time = time()

    create_folder(args.folder_out)
    local_torrents = get_files(args.folder_in)

    s = {
        "total": len(local_torrents),
        "downloaded": 0,
        "already-downloaded": 0,
        "not-found": 0,
        "skipped": 0,
        "error": 0,
    }

    for i, torrent_path in enumerate(local_torrents, 1):
        filename = get_filename(torrent_path)
        try:
            torrent_data = get_torrent_data(torrent_path)
        except AssertionError:
            print(
                f"{Fore.RED}Decoding error. Torrent file is malformed.{Fore.RESET}"
            )
            s["error"] += 1
            continue
        source = get_source(torrent_data)

        print(f"{i}/{s['total']}) {filename}")

        if source == b"OPS" and args.ops_to_red:
            api = red
            new_sources = [b"RED"]
            if args.pth:
                new_sources.append(b"PTH")
        elif source in (b"PTH", b"RED") and args.red_to_ops:
            new_sources = [b"OPS"]
            api = ops
        else:
            print(
                f"{Fore.LIGHTBLACK_EX}Skipped: source is {source.decode('utf-8')}.{Fore.RESET}"
            )
            s["skipped"] += 1
            continue

        for i, new_source in enumerate(new_sources, 0):
            hash = get_new_hash(torrent_data, new_source)
            torrent_details = api.find_torrent(hash)
            status = torrent_details["status"]
            new_source = new_source.decode("utf-8")
            known_errors = ("bad hash parameter", "bad parameters")

            if status == "success":
                torrent_filepath = download_torrent(
                    api, torrent_details, args.folder_out
                )
                if torrent_filepath:
                    print(
                        f"{Fore.LIGHTGREEN_EX}Found with source {new_source} "
                        f"and downloaded as '{get_filename(torrent_filepath)}'.{Fore.RESET}"
                    )
                    s["downloaded"] += 1
                else:
                    print(
                        f"{Fore.LIGHTYELLOW_EX}Found with source {new_source}, "
                        f"but it has already been downloaded.{Fore.RESET}"
                    )
                    s["already-downloaded"] += 1
                break  # Skip the PTH check if found on RED
            elif torrent_details["error"] in known_errors:
                if not args.pth:
                    print(
                        f"{Fore.LIGHTRED_EX}Not found with source {new_source}.{Fore.RESET}"
                    )
                elif args.pth and i == 1:
                    print(
                        f"{Fore.LIGHTRED_EX}Not found with sources "
                        f"{', '.join(x.decode('utf-8') for x in new_sources)}.{Fore.RESET}"
                    )
                s["not-found"] += 1
            else:
                print(
                    f"{Fore.RED}Unexpected error while using source {new_source}{Fore.RESET}"
                    f":\n{str(torrent_details)}"
                )
                s["error"] += 1

    print(
        f"\n{'-' * 50}"
        f"\nAnalyzed {s['total']} local torrents in {time() - start_time:.2f} seconds:\n",
        f"*\t{Fore.LIGHTGREEN_EX}Downloaded for cross-seeding{Fore.RESET}: {s['downloaded']}"
        f" ({s['downloaded']/s['total']*100:.0f}%)\n",
        f"*\t{Fore.LIGHTYELLOW_EX}Already downloaded{Fore.RESET}: {s['already-downloaded']} "
        f"({s['already-downloaded']/s['total']*100:.0f}%)\n",
        f"*\t{Fore.LIGHTRED_EX}Not found{Fore.RESET}: {s['not-found']} "
        f"({s['not-found']/s['total']*100:.0f}%)\n",
        f"*\t{Fore.RED}Errors{Fore.RESET}: {s['error']} "
        f"({s['error']/s['total']*100:.0f}%)\n",
        f"*\t{Fore.LIGHTBLACK_EX}Skipped{Fore.RESET}: {s['skipped']} "
        f"({s['skipped']/s['total']*100:.0f}%)\n",
        f"{'-' * 50}",
        sep=""
    )


if __name__ == "__main__":
    args = get_args()
    config = Config()

    red = RED(config.red_key)
    ops = OPS(config.ops_key)

    main()
