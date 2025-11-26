import json
import sys
import time
import logging
from typing import Optional
import rabbitpy
import rabbitpy.exceptions

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class GGTProcess:
    def __init__(self, process_id: int, initial_value: int, predecessor_id: int, successor_id: int, host: str = 'localhost'):

        self.process_id = process_id
        self.M = initial_value
        self.predecessor_id = predecessor_id
        self.successor_id = successor_id
        self.host = host
        
        # State tracking
        self.iteration = 0
        self.unchanged_rounds = 0
        self.last_M = None
        self.is_running = True
        
        # RabbitMQ setup
        self.connection = None
        self.channel = None
        self.incoming_queue = None
        self.exchange = None
        
    def setup_rabbitmq(self):
        """Setup RabbitMQ connection, channel, and queues."""
        try:
            self.connection = rabbitpy.Connection(f'amqp://guest:guest@{self.host}:5672/%2F')
            self.channel = self.connection.channel()
            
            # Create exchange for GGT communication
            self.exchange = rabbitpy.Exchange(
                self.channel,
                'ggt_exchange',
                exchange_type='direct'
            )
            self.exchange.declare()
            
            # Create incoming queue for this process
            queue_name = f'ggt_process_{self.process_id}'
            self.incoming_queue = rabbitpy.Queue(self.channel, queue_name)
            self.incoming_queue.declare()
            
            # Bind queue to exchange with process ID as routing key
            self.incoming_queue.bind(self.exchange, f'process_{self.process_id}')
            
            logger.info(f'Process {self.process_id}: RabbitMQ setup complete (M={self.M})')
            
        except Exception as e:
            logger.error(f'Process {self.process_id}: RabbitMQ setup failed: {e}')
            raise
 
    def create_message(self, message_type: str, value: int) -> str:
        """
        Create a JSON message.
        
        Args:
            message_type: Type of message ('value', 'query', 'result')
            value: The value to send
            
        Returns:
            JSON-formatted message string
        """
        message = {
            'type': message_type,
            'sender_id': self.process_id,
            'value': value,
            'iteration': self.iteration,
            'timestamp': time.time()
        }
        return json.dumps(message)

    def parse_message(self, message_body: str) -> dict:
        """
        Parse a JSON message.
        
        Args:
            message_body: JSON message string
            
        Returns:
            Parsed message dictionary
        """
        try:
            return json.loads(message_body)
        except json.JSONDecodeError as e:
            logger.error(f'Process {self.process_id}: Failed to parse message: {e}')
            return None

    def send_to_neighbor(self, neighbor_id: int, message: str):
        """
        Send a message to a neighbor.
        
        Args:
            neighbor_id: ID of the neighbor process
            message: JSON message to send
        """
        try:
            msg = rabbitpy.Message(self.channel, message)
            msg.properties['content_type'] = 'application/json'
            msg.publish(self.exchange, f'process_{neighbor_id}')
        except Exception as e:
            logger.error(f'Process {self.process_id}: Failed to send to neighbor {neighbor_id}: {e}')

    def send_to_neighbors(self):
        """Send current M value to both neighbors."""
        message = self.create_message('value', self.M)
        self.send_to_neighbor(self.predecessor_id, message)
        self.send_to_neighbor(self.successor_id, message)
        logger.info(f'Process {self.process_id}: Sent M={self.M} to neighbors')

    def process_incoming_message(self, message_dict: dict):
        """
        Process an incoming message according to the algorithm.
        
        Algorithm:
        if y < M then
            M = mod(M - 1, y) + 1
            send M to all neighbours
        end
        
        Args:
            message_dict: Parsed message dictionary
        """
        if message_dict is None or message_dict['type'] != 'value':
            return
        
        y = message_dict['value']
        sender_id = message_dict['sender_id']
        
        logger.debug(f'Process {self.process_id}: Received y={y} from process {sender_id}')
        
        if y < self.M:
            self.last_M = self.M
            self.M = (self.M - 1) % y + 1
            logger.info(f'Process {self.process_id}: Updated M to {self.M} (was {self.last_M})')
            self.send_to_neighbors()
            self.unchanged_rounds = 0
        else:
            self.unchanged_rounds += 1

    def check_messages(self, timeout: float = 0.1):
        """
        Non-blocking check for incoming messages.
        
        Args:
            timeout: Timeout for message retrieval in seconds
        """
        try:
            if len(self.incoming_queue) > 0:
                message = self.incoming_queue.get()
                if message:
                    message_body = message.body.decode('utf-8')
                    message_dict = self.parse_message(message_body)
                    self.process_incoming_message(message_dict)
                    message.ack()
        # except rabbitpy.exceptions.TimeoutError:
        #     pass
        except Exception as e:
            logger.error(f'Process {self.process_id}: Error checking messages: {e}')

    def run(self, initial_wait: float = 15.0, max_iterations: int = 1000):
        """
        Main loop for the process.
        
        Args:
            initial_wait: Time to wait before sending initial value
            max_iterations: Maximum number of message checks before stopping
        """
        try:
            self.setup_rabbitmq()
            
            # Wait for all processes to be ready
            logger.info(f'Process {self.process_id}: Waiting {initial_wait}s for all processes to start...')
            time.sleep(initial_wait)
            
            # Start algorithm by sending initial M to neighbors
            logger.info(f'Process {self.process_id}: Starting algorithm with M={self.M}')
            self.send_to_neighbors()
            
            # Main message processing loop
            iteration_count = 0
            stable_iterations = 0
            
            while iteration_count < max_iterations and self.is_running:
                self.check_messages(timeout=0.1)
                iteration_count += 1
                
                # Check for convergence (no changes for several iterations)
                if self.last_M == self.M:
                    stable_iterations += 1
                else:
                    stable_iterations = 0
                
                # Optional: Add small delay to prevent busy-waiting
                time.sleep(0.01)
                
            logger.info(f'Process {self.process_id}: Final result M={self.M}')
            
        except KeyboardInterrupt:
            logger.info(f'Process {self.process_id}: Interrupted by user')
        except Exception as e:
            logger.error(f'Process {self.process_id}: Fatal error: {e}')
        finally:
            self.cleanup()

    def cleanup(self):
        """Clean up RabbitMQ resources."""
        try:
            # if self.incoming_queue:
            #     self.incoming_queue.delete()
            # if self.exchange:
            #     self.exchange.delete()
            if self.channel:
                self.channel.close()
            if self.connection:
                self.connection.close()
            logger.info(f'Process {self.process_id}: Cleanup complete')
        except Exception as e:
            logger.error(f'Process {self.process_id}: Cleanup error: {e}')


def main():
    """Entry point for worker process."""
    if len(sys.argv) < 5:
        print('Usage: ggt_worker.py <process_id> <initial_value> <predecessor_id> <successor_id> [host]')
        sys.exit(1)
    
    process_id = int(sys.argv[1])
    initial_value = int(sys.argv[2])
    predecessor_id = int(sys.argv[3])
    successor_id = int(sys.argv[4])
    host = sys.argv[6] if len(sys.argv) > 6 else 'localhost'
    
    process = GGTProcess(
        process_id=process_id,
        initial_value=initial_value,
        predecessor_id=predecessor_id,
        successor_id=successor_id,
        host=host
    )
    
    process.run(initial_wait=15.0, max_iterations=1000)


if __name__ == '__main__':
    main()
