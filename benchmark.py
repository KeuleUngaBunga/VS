import time
from typing import Dict, List
from datastore import Datastore


class Benchmark:

    @staticmethod
    def benchmark_local(impl: Datastore, iterations: int = 1000) -> Dict[str, float]:
        times = {
            "write": [],
            "read": []
        }

        # Benchmark write
        for i in range(iterations):
            start = time.perf_counter()
            impl.write(i, f"test_data_{i}")
            end = time.perf_counter()
            times["write"].append(end - start)

        # Benchmark read
        for i in range(iterations):
            start = time.perf_counter()
            impl.read(i)
            end = time.perf_counter()
            times["read"].append(end - start)

        return times

    @staticmethod
    def calculate_stats(times: List[float]) -> Dict[str, float]:
        if not times:
            return {}

        return {
            "total": sum(times),
            "average": sum(times) / len(times),
            "min": min(times),
            "max": max(times),
            "count": len(times)
        }