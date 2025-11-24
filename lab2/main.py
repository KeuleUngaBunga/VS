#main
import Node
import time

def main():
    Node1 = Node.node(name="example1")
    Node2 = Node.node(name="example2")
    Node3 = Node.node(name="example3")
    
    Node1.declare_queue()
    Node2.declare_queue()
    Node3.declare_queue()

    Node1.produce()
    Node2.produce()
    Node3.produce()
    time.sleep(1)  # Ensure messages are published before consuming
    
    Node1.consume(node_name="example2")
    Node2.consume(node_name="example3")
    Node3.consume(node_name="example1")
    Node1.close()
    Node2.close()
    Node3.close()

if __name__ == "__main__":
    main()