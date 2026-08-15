from __future__ import annotations

import argparse

from services.api.server import serve


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="python -m services.api")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", default=8000, type=int)
    args = parser.parse_args(argv)
    return serve(host=args.host, port=int(args.port))


if __name__ == "__main__":
    raise SystemExit(main())
