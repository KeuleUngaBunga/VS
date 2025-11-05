#!/usr/bin/env python3
"""
RPC Server Application
======================
Starts an RPC server that implements the Datastore interface.

Usage:
    python3 server.py [host] [port]

Default:
    python3 server.py localhost 9999
"""

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

    print("=" * 60)
    print("RPC Server - Datastore Implementation")
    print("=" * 60)
    print(f"Host: {host}")
    print(f"Port: {port}")
    print("\nMethods available:")
    print("  - write(index: int, data: str) -> None")
    print("  - read(index: int) -> str")
    print("\nPress Ctrl+C to stop the server")
    print("=" * 60)
    print()

    try:
        server.start()
    except KeyboardInterrupt:
        print("\n\nShutting down server...")

if __name__ == "__main__":
    main()
