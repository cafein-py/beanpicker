"""The ``transitio`` command line."""

from __future__ import annotations

import argparse
import pathlib


def main(argv=None):
    parser = argparse.ArgumentParser(
        prog="transitio", description="transitio command line"
    )
    commands = parser.add_subparsers(dest="command", required=True)

    edit = commands.add_parser("edit", help="edit a GTFS feed in the local web GUI")
    edit.add_argument("feed", type=pathlib.Path, help="GTFS feed zip")
    edit.add_argument(
        "--osm-pbf",
        type=pathlib.Path,
        help="OSM extract enabling snapped shape drawing",
    )
    edit.add_argument(
        "--network-type",
        default="driving",
        help="pyrosm network type for snapping (default: driving)",
    )
    edit.add_argument("--host", default="127.0.0.1", help="bind address")
    edit.add_argument("--port", type=int, default=8300, help="port")
    edit.add_argument(
        "--allow-remote",
        action="store_true",
        help="allow binding beyond loopback (the editor has no authentication)",
    )

    args = parser.parse_args(argv)

    if args.command == "edit":
        try:
            import uvicorn
        except ImportError:
            parser.error("the GUI requires uvicorn; install transitio[gui]")
        from transitio.edit import FeedEditor
        from transitio.gui import create_app

        if not args.feed.exists():
            parser.error(f"feed not found: {args.feed}")
        if args.host not in ("127.0.0.1", "localhost", "::1") and not args.allow_remote:
            parser.error(
                "the editor has no authentication; refusing a non-loopback "
                "host without --allow-remote"
            )
        editor = FeedEditor(args.feed)
        allowed = None
        if args.allow_remote:
            allowed = ["*"]
        app = create_app(
            editor,
            osm_pbf=args.osm_pbf,
            network_type=args.network_type,
            allowed_hosts=allowed,
        )
        print(f"transitio editor on http://{args.host}:{args.port}")
        uvicorn.run(app, host=args.host, port=args.port, log_level="warning")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
