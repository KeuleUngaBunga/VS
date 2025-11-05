#!/usr/bin/env python3
"""
RPC Client Application with Benchmark
Usage:
    python3 client.py [host] [port]

Default:
    python3 client.py localhost 9999
"""

import sys
import time
import statistics

from benchmark import Benchmark
from clientstub import ClientStub, DatastoreStub
from datastore import DatastoreImpl
from exception import NetworkException, RemoteException


def interactive_mode(stub):
    print("\nInteractive Mode")
    print("Commands:")
    print("  write <index> <data>  - Write data at index")
    print("  read <index>          - Read data from index")
    print("  quit                  - Exit")
    print()

    while True:
        try:
            cmd = input("> ").strip()

            if cmd == "quit":
                break

            parts = cmd.split(maxsplit=2)

            if not parts:
                continue

            if parts[0] == "write" and len(parts) == 3:
                index = int(parts[1])
                data = parts[2]
                stub.write(index, data)
                print(f"Written '{data}' to index {index}")

            elif parts[0] == "read" and len(parts) == 2:
                index = int(parts[1])
                result = stub.read(index)
                print(f"Read from index {index}: '{result}'")

            else:
                print("Invalid command")

        except ValueError as e:
            print(f"Invalid input: {e}")
        except RemoteException as e:
            print(f"Remote error: {e}")
        except NetworkException as e:
            print(f"Network error: {e}")
        except KeyboardInterrupt:
            break
        except Exception as e:
            print(f"Error: {e}")

def benchmark_mode(host, port):
    print("BENCHMARK: Local vs RPC Performance")

    # Create stubs
    client_stub = ClientStub(host, port)
    rpc_stub = DatastoreStub(client_stub)
    local_impl = DatastoreImpl()

    iterations = 1000
    print("Running")

    try:
        print("Benchmarking local")
        local_times = Benchmark.benchmark_local(local_impl, iterations)

        local_write_stats = Benchmark.calculate_stats(local_times["write"])
        local_read_stats = Benchmark.calculate_stats(local_times["read"])

        print(f"   Local write() - Avg: {local_write_stats['average']*1e6:.3f} μs")
        print(f"   Local read()  - Avg: {local_read_stats['average']*1e6:.3f} μs")

        print("Benchmarking RPC")
        rpc_times = {
            "write": [],
            "read": []
        }

        # RPC write benchmark
        for i in range(iterations):
            start = time.perf_counter()
            try:
                rpc_stub.write(i, f"rpc_test_{i}")
                end = time.perf_counter()
                rpc_times["write"].append(end - start)
            except Exception as e:
                print(f"RPC write failed: {e}")
                return

        # RPC read benchmark
        for i in range(iterations):
            start = time.perf_counter()
            try:
                rpc_stub.read(i)
                end = time.perf_counter()
                rpc_times["read"].append(end - start)
            except Exception as e:
                print(f"RPC read failed: {e}")
                return

        rpc_write_stats = Benchmark.calculate_stats(rpc_times["write"])
        rpc_read_stats = Benchmark.calculate_stats(rpc_times["read"])

        print(f"   RPC write()  - Avg: {rpc_write_stats['average']*1e6:.3f} μs")
        print(f"   RPC read()   - Avg: {rpc_read_stats['average']*1e6:.3f} μs")

        write_ratio = rpc_write_stats['average'] / local_write_stats['average']
        read_ratio = rpc_read_stats['average'] / local_read_stats['average']

        print(f"\nWrite Operation:")
        print(f"  Local:   {local_write_stats['average']*1e6:>10.3f} μs (avg)")
        print(f"  RPC:     {rpc_write_stats['average']*1e6:>10.3f} μs (avg)")
        print(f"  Ratio:   {write_ratio:>10.1f}x slower")

        print(f"\nRead Operation:")
        print(f"  Local:   {local_read_stats['average']*1e6:>10.3f} μs (avg)")
        print(f"  RPC:     {rpc_read_stats['average']*1e6:>10.3f} μs (avg)")
        print(f"  Ratio:   {read_ratio:>10.1f}x slower")

        print(f"\nTotal time:")
        print(f"  Local:   {(local_write_stats['total'] + local_read_stats['total'])*1e3:.2f} ms")
        print(f"  RPC:     {(rpc_write_stats['total'] + rpc_read_stats['total'])*1e3:.2f} ms")

    except NetworkException as e:
        print(f"\nNetwork error: {e}")
    except Exception as e:
        print(f"\nError during benchmark: {e}")
    finally:
        client_stub.close()

def main():
    host = sys.argv[1] if len(sys.argv) > 1 else "localhost"
    port = int(sys.argv[2]) if len(sys.argv) > 2 else 9999

    print(f"Connecting to {host}:{port}")

    client_stub = ClientStub(host, port)
    stub = DatastoreStub(client_stub)

    try:
        # Show menu
        print("  1. Interactive mode")
        print("  2. Run benchmark")
        print("  3. Exit")
        print()

        while True:
            choice = input("Select option (1-3): ").strip()

            if choice == "1":
                interactive_mode(stub)
            elif choice == "2":
                benchmark_mode(host, port)
            elif choice == "3":
                break
            else:
                print("Invalid option")

    except RemoteException as e:
        print(f"Remote error: {e}")
    except NetworkException as e:
        print(f"Connection failed: {e}")
        print(f"Make sure the server is running at {host}:{port}")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        client_stub.close()
        print("Disconnected")

if __name__ == "__main__":
    main()
