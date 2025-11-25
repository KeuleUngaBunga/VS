import rabbitpy
import msg_serializer

class node():
    def __init__(self, name, val):
        
        self.decoder = msg_serializer.node_decoder()
        self.name = name
        self.val = val
        self.connection = rabbitpy.Connection()  # Connect to RabbitMQ server
        self.channel = self.connection.channel()  # Create new channel on the connection
        # Declare queue with the same name as the node
        self.queue = rabbitpy.Queue(self.channel, self.name)
        self.queue.declare()
        
        # Declare shared exchange (used by all nodes)
        self.exchange = rabbitpy.Exchange(self.channel, 'exchange')
        self.exchange.declare()

        
    
    def produce(self):#1 default 
        # Bind OWN queue to unique routing key (so messages go to this node's queue)
        routing_key = f"key_to_{self.name}"
        self.queue.bind(self.exchange, routing_key)
        
        # Send message with routing key
        msg = self.decoder.encode(node_id=self.name, value=self.val)
        message = rabbitpy.Message(self.channel, msg)
        message.publish(self.exchange, routing_key)  # Publish with unique routing key
        
        print(f"[Producer - {self.name}] Message published ")
   
    def consume(self, queue_name):            
        """Read messages from another node's queue"""
        #debug:
        #print(f"[Consumer - {self.name}] Listening for messages from queue '{queue_name}'...")
        
        # Access another queue by name (it was created by that node)
        other_queue = rabbitpy.Queue(self.channel, queue_name)
        
        # Fetch messages from that queue
        while len(other_queue) > 0:
            message = other_queue.get()
            data=self.decoder.decode(message.body)
            if(data.get("type")=="node_message"):
                val=data.get("value")
                if val < self.val:
                    self.val = ((self.val-1)% val) + 1  
                self.produce()
                print(f"[{self.name}] Received: {val}")
            message.ack()
        #debug:
        #print(f"[Consumer - {self.name}] Done")

    def close(self):
        self.connection.close()
        print(f"[Node] Closed connection from {self.name}")