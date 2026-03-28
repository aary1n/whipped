from __future__ import annotations

import argparse

from whipped.webapp import run_server


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run the Whipped localhost web UI.")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8000)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    run_server(host=args.host, port=args.port)


if __name__ == "__main__":
    main()
