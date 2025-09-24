from Server import Server
from Client import Client
import sys

if __name__ == "__main__":
    if len(sys.argv) != 2:
        if len(sys.argv) == 3 and sys.argv[2].lower() != "--debug" and sys.argv[1].lower() != "client":
            print("Usage: python main.py [client|server] [--debug]")
            sys.exit(1)
    if sys.argv[1].lower() == "client":
        debug = sys.argv[2].lower() == "--debug" if len(sys.argv) >= 3 else False
        client = Client(debug)
    elif sys.argv[1].lower() == "server":
        server = Server()
    else:
        print("Invalid argument. Use 'client' or 'server'.")