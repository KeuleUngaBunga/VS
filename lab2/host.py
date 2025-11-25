"""
Simple RabbitMQ Management Host

Responsibilities:
1. Listen on a management queue for client registrations (JSON)
2. Keep track of registered clients
3. Distribute nodes equally across registered clients
4. Send JSON commands to each client with their assigned node IDs
5. Coordinate node startup (signal clients to start producing)
"""

import json
import time
import threading
import rabbitpy


class Host:
    def __init__(self, host='localhost', mgmt_queue='host_mgmt', total_nodes=None):
        """
        Initialize the Host.
        
        Args:
            host: RabbitMQ host (default 'localhost')
            mgmt_queue: Queue name for management messages
            total_nodes: Total number of nodes to spawn (can be None, set later)
        """
        self.amqp_url = f'amqp://guest:guest@{host}:5672/%2F'
        self.mgmt_queue = mgmt_queue
        self.total_nodes = total_nodes
        self._running = False
        
        # Registries
        self.registered_clients = {}  # client_id -> {'queue': queue_name, 'info': info}
        self.node_allocation = {}      # client_id -> [node_ids]
        
        # RabbitMQ connection
        self.connection = None
        self.channel = None
        self.exchange = None
        self.queue = None
        
    def _setup_rabbitmq(self):
        """Setup RabbitMQ connection and management queue."""
        self.connection = rabbitpy.Connection(self.amqp_url)
        self.channel = self.connection.channel()
        
        # Management exchange and queue
        self.exchange = rabbitpy.Exchange(self.channel, 'host_exchange', exchange_type='direct')
        self.exchange.declare()
        
        self.queue = rabbitpy.Queue(self.channel, self.mgmt_queue)
        self.queue.declare()
        self.queue.bind(self.exchange, self.mgmt_queue)
        
        print(f"[Host] RabbitMQ setup complete. Listening on queue '{self.mgmt_queue}'")
    
    def _handle_registration(self, msg_data):
        """Handle client registration message."""
        client_id = msg_data.get('client_id')
        client_queue = msg_data.get('client_queue')
        info = msg_data.get('info', {})
        
        if not client_id or not client_queue:
            print("[Host] ERROR: Invalid registration message (missing client_id or client_queue)")
            return
        
        self.registered_clients[client_id] = {
            'queue': client_queue,
            'info': info
        }
        print(f"[Host] Client registered: {client_id} (queue: {client_queue})")
    
    def distribute_nodes(self):
        """Distribute nodes equally across registered clients."""
        if self.total_nodes is None or self.total_nodes <= 0:
            print("[Host] ERROR: total_nodes not set or invalid")
            return False
        
        num_clients = len(self.registered_clients)
        if num_clients == 0:
            print("[Host] ERROR: No clients registered")
            return False
        
        # Calculate distribution
        nodes_per_client = self.total_nodes // num_clients
        extra_nodes = self.total_nodes % num_clients
        
        node_id = 0
        for i, client_id in enumerate(sorted(self.registered_clients.keys())):
            # Some clients get one extra node
            count = nodes_per_client + (1 if i < extra_nodes else 0)
            node_ids = list(range(node_id, node_id + count))
            self.node_allocation[client_id] = node_ids
            node_id += count
            
            print(f"[Host] Allocated {len(node_ids)} nodes to {client_id}: {node_ids}")
        
        print(f"[Host] Node distribution complete: {self.total_nodes} nodes across {num_clients} clients")
        return True
    
    def send_node_spawn_command(self):
        """Send node spawn commands to all registered clients."""
        self.distribute_nodes()
        
        for client_id, node_ids in self.node_allocation.items():
            client_info = self.registered_clients[client_id]
            client_queue = client_info['queue']
            
            # Create spawn command
            cmd = {
                'type': 'spawn_nodes',
                'node_ids': node_ids,
                'total_nodes': self.total_nodes,
                'client_id': client_id
            }
            
            # Send to client's queue
            msg = rabbitpy.Message(self.channel, json.dumps(cmd))
            msg.publish(self.exchange, client_queue)
            
            print(f"[Host] Sent spawn command to {client_id}: {len(node_ids)} nodes (IDs: {node_ids})")
        
        return True
    
    def send_start_producing_signal(self):
        """Signal all clients to start nodes producing messages."""
        for client_id, client_info in self.registered_clients.items():
            client_queue = client_info['queue']
            
            cmd = {
                'type': 'start_producing',
                'total_nodes': self.total_nodes
            }
            
            msg = rabbitpy.Message(self.channel, json.dumps(cmd))
            msg.publish(self.exchange, client_queue)
            
            print(f"[Host] Sent start_producing signal to {client_id}")
        
        return True
    
    def listen_for_registrations(self, max_clients=1):
        """
        Listen for client registrations in a non-blocking loop.

        The function returns when either `duration` seconds have passed (if provided)
        or when the number of registered clients reaches `max_clients` (if provided).

        Args:
            max_clients: Maximum number of clients to wait for (None = no limit)
            duration: Listen for X seconds (None = no timeout)
        """
        self._setup_rabbitmq()
        self._running = True

        print(f"[Host] Listening for client registrations (max_clients={max_clients})...")
        try:
            while self._running:

                # check if reached max clients
                if max_clients is not None and len(self.registered_clients) >= max_clients:
                    print(f"[Host] Reached max_clients={max_clients}. Stopping registration.")
                    return

                # process available messages
                while len(self.queue) > 0:
                    message = self.queue.get()
                    try:
                        data = json.loads(message.body.decode())
                        if data.get('type') == 'register':
                            self._handle_registration(data)
                        else:
                            print('[Host] Ignoring non-register message on mgmt queue')
                    except json.JSONDecodeError:
                        print("[Host] ERROR: Received invalid JSON")
                    except Exception as e:
                        print(f"[Host] ERROR processing message: {e}")
                    finally:
                        try:
                            message.ack()
                        except Exception:
                            pass

                # small sleep to avoid busy loop
                time.sleep(0.1)
        except KeyboardInterrupt:
            print("[Host] Interrupted")
        finally:
            # do not close connections here; orchestrate will continue
            return
    
    def stop(self):
        """Stop the host and close connections."""
        self._running = False
        if self.connection:
            try:
                self.connection.close()
                print("[Host] Connection closed")
            except Exception:
                pass
    
    def orchestrate(self, total_nodes, max_clients=1):
        """
        Full orchestration: wait for registrations, distribute nodes, spawn, and signal produce.
        
        Args:
            total_nodes: Total number of nodes to spawn
            registration_wait_time: Seconds to wait for client registrations
        """
        self.total_nodes = total_nodes
        
        # Listen for registrations (non-blocking). If max_clients provided, stop when reached.
        print(f"[Host] Waiting for up to {max_clients} client registrations (no timeout)...")
        self.listen_for_registrations(max_clients=max_clients)
        
        
        print(f"[Host] Registration phase complete. {len(self.registered_clients)} clients registered.")
        
        if len(self.registered_clients) == 0:
            print("[Host] ERROR: No clients registered. Exiting.")
            return
                
        # Send spawn commands
        if not self.send_node_spawn_command():
            return
        
        time.sleep(2)
        
        # Signal to start producing
        if not self.send_start_producing_signal():
            return
        print("end communication?")
        close=input()
        '''
        if close=="close":
            #stop clients
            self.stop()
        print("[Host] Orchestration complete. Nodes should now be communicating.")
        '''

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='RabbitMQ Management Host')
    parser.add_argument('--host', default='localhost', help='RabbitMQ host')
    parser.add_argument('--total-nodes', type=int, default=12, help='Total nodes to spawn')
    parser.add_argument('--registration-wait', type=int, default=10, help='Seconds to wait for registrations')
    
    args = parser.parse_args()
    
    host = Host(host=args.host, total_nodes=args.total_nodes)
    host.orchestrate(args.total_nodes, registration_wait_time=args.registration_wait)
    
    print("[Host] Exiting.")


if __name__ == '__main__':
    main()
