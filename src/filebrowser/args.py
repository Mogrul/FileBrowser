from argparse import ArgumentParser, Namespace

def _get_args() -> Namespace:
    parser = ArgumentParser()

    parser.add_argument(
        "--host",
        default="127.0.0.1",
        help="The host where the server is running",
    )

    parser.add_argument(
        "--port",
        default=80,
        help="The port where the server is running",
    )

    return parser.parse_args()

class Args:
    def __init__(self) -> None:
        _args = _get_args()

        self.host = _args.host
        self.port = _args.port

args = Args()