from frigg import app
import argparse

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Run the frigg server.')
    parser.add_argument('-d', '--debug', action='store_true',
                        default=True, help='Run the server in debug mode.')
    parser.add_argument('-H', '--host', default='127.0.0.1',
                        help='The host to bind the server to.')
    parser.add_argument('-p', '--port', type=int, default=5000,
                        help='The port to bind the server to.')
    args = parser.parse_args()
    app.run(debug=args.debug, host=args.host, port=args.port)
