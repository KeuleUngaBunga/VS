"""
RabbitMQ Client for distributed node management

Responsibilities:
1. Register with the host via JSON
2. Listen for node spawn commands
3. Instantiate Node objects for assigned node IDs
4. Listen for start_producing signal
5. Make nodes communicate in a loop (circular: node_i → node_(i+1 % total))
"""

import json
import time
import threading
import rabbitpy
import Node
import msg_serializer

class Client:
    def __init__(self, client_id, host='localhost', client_queue=None):
        """
        Initialize the Client.
        
        Args:
            client_id: Unique client identifier
            host: RabbitMQ host
            client_queue: Queue name for this client (default: client_{client_id})
        """
        self.decoder = msg_serializer.connect_decoder()
        self.client_id = client_id
        self.amqp_url = f'amqp://guest:guest@{host}:5672/%2F'
        self.client_queue = client_queue or f'client_{client_id}'
        self.mgmt_queue = 'host_mgmt'
        
        # State
        self.nodes = {}         # node_id -> Node object
        self.node_ids = []      # Assigned node IDs
        self.total_nodes = None # Total nodes in system
        self._running = False
        # Events to wait for spawn and start signals
        self.spawn_event = threading.Event()
        self.start_event = threading.Event()
        
        # RabbitMQ
        self.connection = None
        self.channel = None
        self.exchange = None
        self.queue = None
    
    def _setup_rabbitmq(self):
        """Setup RabbitMQ connection and client queue."""
        self.connection = rabbitpy.Connection(self.amqp_url)
        self.channel = self.connection.channel()
        
        # Management exchange
        self.exchange = rabbitpy.Exchange(self.channel, 'host_exchange', exchange_type='direct')
        self.exchange.declare()
        
        # Client's own queue
        self.queue = rabbitpy.Queue(self.channel, self.client_queue)
        self.queue.declare()
        self.queue.bind(self.exchange, self.client_queue)
        
        print(f"[Client {self.client_id}] RabbitMQ setup complete. Queue: {self.client_queue}")
    
    def register_with_host(self):
        """Register this client with the host."""
        self._setup_rabbitmq()
    
        msg = self.decoder.encode_register(
            client_id=self.client_id,
            client_queue=self.client_queue,
        )
        message = rabbitpy.Message(self.channel, msg)
        message.publish(self.exchange, self.mgmt_queue)
        
        print(f"[Client {self.client_id}] Registration message sent to host")
    
    def _create_nodes(self, node_ids,node_vals):
        """Create Node objects for assigned node IDs."""
        i=0
        for node_id in node_ids:
            node_name = f"node_{node_id}"
            try:
                n = Node.node(name=node_name, val=node_vals[i])
                n.produce()
                i+=1
                self.nodes[node_id] = n
                print(f"[Client {self.client_id}] Created node: {node_name}")
            except Exception as e:
                print(f"[Client {self.client_id}] ERROR creating node {node_name}: {e}")
    
    def _handle_spawn_nodes(self, cmd):
        """Handle spawn_nodes command from host."""
        node_ids = cmd.get('node_ids', [])
        self.total_nodes = cmd.get('total_nodes')
        unique_node_vals = cmd.get('node_vals', [])
        print(f"[Client {self.client_id}] Received spawn command for {len(node_ids)} nodes: {node_ids}")
        self.node_ids = node_ids
        self._create_nodes(node_ids,unique_node_vals)
        print(f"[Client {self.client_id}] All nodes created successfully")
        # Signal that spawn has completed
        self.spawn_event.set()
    
    
    def listen_for_commands(self):
        """Listen for commands from host (blocking)."""
        self._running = True
        print(f"[Client {self.client_id}] Listening for commands from host...")
        
        try:
            while self._running:
                while len(self.queue) > 0:
                    message = self.queue.get()
                    try:
                        cmd = self.decoder.decode(message.body)
                        cmd_type = cmd.get('type')
                        
                        if cmd_type == 'spawn_nodes':
                            self._handle_spawn_nodes(cmd)
                        else:
                            print(f"[Client {self.client_id}] Unknown command type: {cmd_type}")
                    except json.JSONDecodeError:
                        print(f"[Client {self.client_id}] ERROR: Invalid JSON received")
                    except Exception as e:
                        print(f"[Client {self.client_id}] ERROR processing command: {e}")
                    
                    message.ack()
                
                time.sleep(0.1)
        except KeyboardInterrupt:
            print(f"[Client {self.client_id}] Interrupted")
        finally:
            self.stop()
    
    def run_node_communication(self):
        """
        Run circular communication between nodes:
        - node_i produces to node_(i+1 % total)
        - Each node receives from node_(i-1 % total)
        
        This runs in a loop until interrupted.
        """
        if not self.node_ids or self.total_nodes is None:
            print(f"[Client {self.client_id}] ERROR: Nodes not ready. Wait for spawn and start commands.")
            return
        
        print(f"[Client {self.client_id}] Starting node communication loop...")
        start_time = time.time()
        try:
            while self._running:
                crnt_time = time.time()
                if crnt_time - start_time > 15:  # Run for 30 seconds
                    print(f"[Client {self.client_id}] Reached 30 seconds of communication. Stopping.")
                    self.close_nodes()
                    self.stop()
                    break
                for node_id in self.node_ids:
                    n = self.nodes[node_id]
                    
                    # Produce: send message to next node in circular order
                    
                    
                    # Consume: read from previous and next? node in circular order
                    
                    #---------------------------------------------
                    #prev_node_id= node_id-1
                    #if(prev_node_id<0):
                    #    prev_node_id=self.total_nodes-1
                    next_node_id= (node_id+1)
                    if(next_node_id>=self.total_nodes):
                        next_node_id=0
                    #prev_node_name = f"node_{prev_node_id}"
                    next_node_name = f"node_{next_node_id}"
                    #n.consume(prev_node_name)
                    n.consume(next_node_name)
                    #ggT=n.get_ggT()
                    #n.produce(num=ggT)
                    #----------------------------------------------
                time.sleep(1)
        except KeyboardInterrupt:
            print(f"[Client {self.client_id}] Communication loop interrupted")
        finally:
            self.close_nodes()
    
    def close_nodes(self):
        """Close all nodes."""
        for node_id, n in self.nodes.items():
            try:
                n.close()
            except Exception as e:
                print(f"[Client {self.client_id}] ERROR closing node {node_id}: {e}")
    
    def stop(self):
        """Stop the client."""
        self._running = False
        if self.connection:
            try:
                self.connection.close()
            except Exception:
                pass
    
    def run(self):
        """Main client loop: register, listen for commands, then communicate."""
        try:
            # Register
            self.register_with_host()
            time.sleep(0.5)
            
            # Listen for commands in a background thread
            cmd_thread = threading.Thread(target=self.listen_for_commands, daemon=True)
            cmd_thread.start()
            
            # Wait for spawn command (blocks until spawn received)
            print(f"[Client {self.client_id}] Waiting for spawn command from host...")
            self.spawn_event.wait()  # block until spawn_event.set()

            if not self.node_ids:
                print(f"[Client {self.client_id}] ERROR: No nodes were spawned")
                return
            # Run node communication
            self.run_node_communication()
        
        except Exception as e:
            print(f"[Client {self.client_id}] ERROR in run: {e}")
        finally:
            self.stop()


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='RabbitMQ Client for node management')
    parser.add_argument('--client-id', required=True, help='Unique client ID')
    parser.add_argument('--host', default='localhost', help='RabbitMQ host')
    parser.add_argument('--client-queue', help='Queue name for this client (default: client_{client_id})')
    
    args = parser.parse_args()
    
    client = Client(
        client_id=args.client_id,
        host=args.host,
        client_queue=args.client_queue
    )
    client.run()


if __name__ == '__main__':
    main()
