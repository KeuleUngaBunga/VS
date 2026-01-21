#!/usr/bin/env python3
"""
Replicated Datastore Server
Supports running multiple instances on different ports
"""

import sys
import time
from datastore import DatastoreImpl
from rpc_server import RPCServer


def main():
    host = sys.argv[1] if len(sys.argv) > 1 else "localhost"
    port = int(sys.argv[2]) if len(sys.argv) > 2 else 9999

    impl = DatastoreImpl()
    server = RPCServer(host, port, impl)

    print(f"Starting Replicated Datastore Server")
    print(f"Host: {host}")
    print(f"Port: {port}")
    print("\nMethods available:")
    print("  - write(index: int, data: str) -> None")
    print("  - read(index: int) -> str")
    print("\nRun multiple instances with different ports:")
    print(f"  Terminal 1: python3 replicated_server.py {host} 9999")
    print(f"  Terminal 2: python3 replicated_server.py {host} 9998")
    print(f"  Terminal 3: python3 replicated_server.py {host} 9997")

    try:
        server.start()
    except KeyboardInterrupt:
        print("\nShutting down server...")


if __name__ == "__main__":
    main()
