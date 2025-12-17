#!/usr/bin/env python3
"""
Test-Skript für das GGT Distributed System.
Startet den Coordinator mit Mock-Agents für lokales Testen.
"""

import sys
import time
import threading
import logging
from coordinator1 import Coordinator
from agent import Agent


def setup_logging():
    """Setup Logging für alle Komponenten"""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )


def test_single_value():
    """Test mit einem einzelnen Wert (sollte fehlschlagen)"""
    print("\n" + "=" * 60)
    print("TEST 1: Single Value (should fail)")
    print("=" * 60)
    
    coordinator = Coordinator(0, "localhost")
    try:
        results = coordinator.start_ggt_computation([42], registration_timeout=2)
    except:
        pass
    finally:
        coordinator.cleanup()


def test_two_values():
    """Test mit zwei Werten"""
    print("\n" + "=" * 60)
    print("TEST 2: Two Values (12, 18)")
    print("=" * 60)
    
    # Starte Coordinator
    coordinator = Coordinator(0, "localhost")
    coordinator_thread = threading.Thread(target=coordinator.start, daemon=True)
    coordinator_thread.start()
    time.sleep(1)
    
    # Starte 2 Agents
    agents = []
    for i in range(1, 3):
        agent = Agent(i, coordinator_id=0, capacity=10, host="localhost")
        thread = threading.Thread(target=agent.start, daemon=True)
        thread.start()
        agents.append(agent)
        time.sleep(0.5)
    
    # Starte Berechnung
    time.sleep(2)
    results = coordinator.start_ggt_computation([12, 18], registration_timeout=5)
    
    print("\nResults:", results)
    print("Expected: Both processes should converge to 6 (GCD of 12 and 18)")
    
    # Cleanup
    coordinator.cleanup()
    for agent in agents:
        agent.cleanup()
    time.sleep(1)


def test_three_values():
    """Test mit drei Werten"""
    print("\n" + "=" * 60)
    print("TEST 3: Three Values (12, 18, 24)")
    print("=" * 60)
    
    # Starte Coordinator
    coordinator = Coordinator(0, "localhost")
    coordinator_thread = threading.Thread(target=coordinator.start, daemon=True)
    coordinator_thread.start()
    time.sleep(1)
    
    # Starte 3 Agents
    agents = []
    for i in range(1, 4):
        agent = Agent(i, coordinator_id=0, capacity=10, host="localhost")
        thread = threading.Thread(target=agent.start, daemon=True)
        thread.start()
        agents.append(agent)
        time.sleep(0.5)
    
    # Starte Berechnung
    time.sleep(2)
    results = coordinator.start_ggt_computation([12, 18, 24], registration_timeout=5)
    
    print("\nResults:", results)
    print("Expected: All processes should converge to 6 (GCD of 12, 18, 24)")
    
    # Cleanup
    coordinator.cleanup()
    for agent in agents:
        agent.cleanup()
    time.sleep(1)


def test_load_balancing():
    """Test Load Balancing mit unterschiedlichen Anzahlen"""
    print("\n" + "=" * 60)
    print("TEST 4: Load Balancing (5 processes, 2 agents)")
    print("=" * 60)
    
    # Starte Coordinator
    coordinator = Coordinator(0, "localhost")
    coordinator_thread = threading.Thread(target=coordinator.start, daemon=True)
    coordinator_thread.start()
    time.sleep(1)
    
    # Starte 2 Agents für 5 Prozesse
    agents = []
    for i in range(1, 3):
        agent = Agent(i, coordinator_id=0, capacity=10, host="localhost")
        thread = threading.Thread(target=agent.start, daemon=True)
        thread.start()
        agents.append(agent)
        time.sleep(0.5)
    
    # Starte Berechnung mit 5 Werten
    time.sleep(2)
    values = [10, 15, 20, 25, 30]
    results = coordinator.start_ggt_computation(values, registration_timeout=5)
    
    print(f"\nResults: {results}")
    print("Expected: 5 processes distributed as: Agent 1: 3 processes, Agent 2: 2 processes")
    print(f"Expected result: All converge to 5 (GCD of {values})")
    
    # Cleanup
    coordinator.cleanup()
    for agent in agents:
        agent.cleanup()
    time.sleep(1)


def test_prime_numbers():
    """Test mit Primzahlen (GCD sollte 1 sein)"""
    print("\n" + "=" * 60)
    print("TEST 5: Prime Numbers (7, 11, 13)")
    print("=" * 60)
    
    # Starte Coordinator
    coordinator = Coordinator(0, "localhost")
    coordinator_thread = threading.Thread(target=coordinator.start, daemon=True)
    coordinator_thread.start()
    time.sleep(1)
    
    # Starte 2 Agents
    agents = []
    for i in range(1, 3):
        agent = Agent(i, coordinator_id=0, capacity=10, host="localhost")
        thread = threading.Thread(target=agent.start, daemon=True)
        thread.start()
        agents.append(agent)
        time.sleep(0.5)
    
    # Starte Berechnung
    time.sleep(2)
    results = coordinator.start_ggt_computation([7, 11, 13], registration_timeout=5)
    
    print("\nResults:", results)
    print("Expected: All processes should converge to 1 (GCD of primes)")
    
    # Cleanup
    coordinator.cleanup()
    for agent in agents:
        agent.cleanup()
    time.sleep(1)


def main():
    """Führe alle Tests aus"""
    setup_logging()
    
    print("\n" + "=" * 60)
    print("GGT DISTRIBUTED SYSTEM - TEST SUITE")
    print("=" * 60)
    
    tests = [
        ("2-Value Test", test_two_values),
        ("3-Value Test", test_three_values),
        ("Load Balancing Test", test_load_balancing),
        ("Prime Numbers Test", test_prime_numbers),
    ]
    
    for test_name, test_func in tests:
        try:
            test_func()
            print(f"\n✓ {test_name} PASSED")
        except Exception as e:
            print(f"\n✗ {test_name} FAILED: {e}")
            import traceback
            traceback.print_exc()
        
        time.sleep(2)  # Pause zwischen Tests
    
    print("\n" + "=" * 60)
    print("TEST SUITE COMPLETE")
    print("=" * 60)


if __name__ == "__main__":
    main()
