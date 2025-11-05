#!/usr/bin/env python3
import sys
import time

from datastore import DatastoreImpl
from rpc_server import RPCServer

def main():
    # Parse arguments
    host = sys.argv[1] if len(sys.argv) > 1 else "localhost"
    port = int(sys.argv[2]) if len(sys.argv) > 2 else 9999

    # Create server
    impl = DatastoreImpl()
    server = RPCServer(host, port, impl)

    print(f"Host: {host}")
    print(f"Port: {port}")
    print("\nMethods available:")
    print("  - write(index: int, data: str) -> None")
    print("  - read(index: int) -> str")

    try:
        server.start()
    except KeyboardInterrupt:
        print("Shutting down server...")

if __name__ == "__main__":
    main()
