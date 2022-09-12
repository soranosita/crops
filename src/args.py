import argparse


def get_formatter(prog):
    return argparse.HelpFormatter(prog)


def get_args():
    name = "crops"
    description = "an open source cross-seeder for RED & OPS"
    parser = argparse.ArgumentParser(
        prog=name,
        description=description,
        formatter_class=get_formatter,
        add_help=False,
    )

    support = parser.add_argument_group(title="support")
    directories = parser.add_argument_group(title="directories")
    modes = parser.add_argument_group(title="modes").add_mutually_exclusive_group(
        required=True
    )
    extras = parser.add_argument_group(title="extras")

    support.add_argument(
        "-h",
        "--help",
        action="help",
        default=argparse.SUPPRESS,
        help="show this help message and exit",
    )

    directories.add_argument(
        "-i",
        "--folder-in",
        type=str,
        required=True,
        help="folder with the .torrent files to check",
    )
    directories.add_argument(
        "-o",
        "--folder_out",
        type=str,
        required=True,
        help="folder where cross-seedable .torrent files will be saved",
    )

    modes.add_argument(
        "--ops-to-red",
        action="store_true",
        help="consider torrents with the OPS source flag",
    )
    modes.add_argument(
        "--red-to-ops",
        action="store_true",
        help="consider torrents with the RED source flag",
    )

    extras.add_argument(
        "--pth",
        action="store_true",
        help="calculate infohashes with the PTH source flag too",
    )
    extras.add_argument(
        "--download",
        action="store_true",
        help="download final .torrent files instead of generating them",
    )

    return parser.parse_args()
