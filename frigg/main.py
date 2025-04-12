from frigg import app
import argparse

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run the frigg server.")
    parser.add_argument(
        "-D",
        "--no-debug",
        action="store_true",
        help="Do not run the server in debug mode",
    )
    parser.add_argument(
        "-H", "--host", default="0.0.0.0", help="The host to bind the server to"
    )
    parser.add_argument(
        "-p", "--port", type=int, default=5000, help="The port to bind the server to"
    )
    args, _ = parser.parse_known_args()
    app.run(debug=not args.no_debug, host=args.host, port=args.port)
