import argparse


def get_formatter(prog):
    return argparse.HelpFormatter(prog)


def get_args():
    name = "crops"
    description = "an open source cross-seeder for RED and OPS"
    parser = argparse.ArgumentParser(
        prog=name,
        description=description,
        formatter_class=get_formatter,
        add_help=False
    )

    h = parser.add_argument_group(title="support")
    d = parser.add_argument_group(title="directories")
    t = parser.add_argument_group(title="modes")
    tg = t.add_mutually_exclusive_group(required=True)
    o = parser.add_argument_group(title="extras")

    # Help
    h.add_argument(
        "-h", "--help", action="help", default=argparse.SUPPRESS,
        help="show this help message and exit"
    )

    # Directories
    d.add_argument(
        "-i", "--folder-in", type=str, required=True,
        help="folder with the .torrent files to check"
    )
    d.add_argument(
        "-o", "--folder_out", type=str, required=True,
        help="folder where cross-seedable .torrent files will be saved"
    )

    # Modes
    tg.add_argument(
        "--ops-to-red", action="store_true",
        help="consider torrents with the OPS source flag"
    )
    tg.add_argument(
        "--red-to-ops", action="store_true",
        help="consider torrents with the RED source flag"
    )

    # Extras
    o.add_argument(
        "--pth", action="store_true",
        help="calculate infohashes with the PTH source flag too"
    )

    o.add_argument(
        "--announce", type=str,
        help="use announce URL to build final .torrent file"
    )

    return parser.parse_args()
