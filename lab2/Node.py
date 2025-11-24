import rabbitpy

class node():
    def __init__(self, name):
        self.name = name
        #self.host = host
        self.connection = rabbitpy.Connection()  # Connect to RabbitMQ server
        self.channel = self.connection.channel()  # Create new channel on the connection

    def declare_queue(self):
        self.queue1 = rabbitpy.Queue(self.channel, self.name)  # Create 1st queue
        self.queue1.declare()
        
  
    def produce(self):
        exchange = rabbitpy.Exchange(self.channel, 'exchange')  # Create an exchange
        exchange.declare()
        self.queue1.bind(exchange, 'example-key')  # Bind queue1 to a single key
        
        # Send messages to both queues
        test_msg='Test message from '+self.name#test message for Queue 

        message1 = rabbitpy.Message(self.channel, test_msg)
        message1.publish(exchange, 'example-key')  # Publish to Q1
        
        print("[Producer] Messages published")
        #connection.close()
   
    def consume(self, node_name):            
        # Declare queues (same as producer)

        print("[Consumer] Listening for messages...")
        self.queue2  =  rabbitpy.Queue(self.channel,  node_name)
    
        # Fetch messages from Queue 2
        while len(self.queue2) > 0:
            message = self.queue2.get()
            # print both the node name and the message body
            # using an f-string is simple and readable
            print(f"Message from {self.name}: {message.body.decode()}")
            message.ack()
        
        print("[Consumer] Done")

    def close(self):
        #print("[Node] Closing connection")
        self.connection.close()
        print("[Node] Closed from "+self.name)