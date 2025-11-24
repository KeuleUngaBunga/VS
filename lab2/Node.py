import rabbitpy

class node():
    def __init__(self, name):
        self.name = name
        self.connection = rabbitpy.Connection()  # Connect to RabbitMQ server
        self.channel = self.connection.channel()  # Create new channel on the connection
        # Declare queue with the same name as the node
        self.queue = rabbitpy.Queue(self.channel, self.name)
        self.queue.declare()
        
        # Declare shared exchange (used by all nodes)
        self.exchange = rabbitpy.Exchange(self.channel, 'exchange')
        self.exchange.declare()

        
  
    def produce(self,num=1):#1 default 
        # Bind OWN queue to unique routing key (so messages go to this node's queue)
        routing_key = f"key_to_{self.name}"
        self.queue.bind(self.exchange, routing_key)
        
        # Send message with routing key
        msg = 'Message from ' + self.name + ' with number ' + str(num)
        message = rabbitpy.Message(self.channel, msg)
        message.publish(self.exchange, routing_key)  # Publish with unique routing key
        
        print(f"[Producer - {self.name}] Message published to routing key '{routing_key}'")
   
    def consume(self, queue_name):            
        """Read messages from another node's queue"""
        #debug:
        #print(f"[Consumer - {self.name}] Listening for messages from queue '{queue_name}'...")
        
        # Access another queue by name (it was created by that node)
        other_queue = rabbitpy.Queue(self.channel, queue_name)
        
        # Fetch messages from that queue
        while len(other_queue) > 0:
            message = other_queue.get()
            print(f"[{self.name}] Received: {message.body.decode()}")
            message.ack()
        #debug:
        #print(f"[Consumer - {self.name}] Done")

    def close(self):
        self.connection.close()
        print(f"[Node] Closed connection from {self.name}")