#main
import Node
import time

def main():
    #simple test with 3 nodes
    Node1 = Node.node(name="example1")
    Node2 = Node.node(name="example2")
    Node3 = Node.node(name="example3")
    

    Node1.produce()
    Node2.produce()
    Node3.produce()
    time.sleep(1)  # Ensure messages are published before consuming

    Node1.consume(queue_name="example2")
    Node2.consume(queue_name="example3")
    Node3.consume(queue_name="example1")
    Node1.close()
    Node2.close()
    Node3.close()
    
def main_circular():
    #test main
    #--------------------------------
    #input
    print("All nodes have finished processing.")
    print("how many nodes for testing?")
    num_nodes = int(input())
    nums = []
    for i in range(num_nodes):
        nums.append(int(input(f"Enter number for node {i}: ")))
    print(f"Testing with {num_nodes} nodes.")
    #input end
    #------------------------------------
    nodes = []

    for i in range(num_nodes):# i nodes erstellen und in queue schreiben
        node = Node.node(name=f"test_node_{i}")
        nodes.append(node)
        node.produce(num=nums[i])
    time.sleep(1)  # Ensure messages are published before consuming

    for i in range(num_nodes):# i nodes konsumieren von i+1 node
        #node = Node.node(name=f"test_node_{i}")
        node = nodes[i]
        if i == num_nodes-1:
            node.consume(queue_name="test_node_0")
        else:
            node.consume(queue_name=f"test_node_{i + 1}")
        node.close()
    print("All nodes have finished processing.")

if __name__ == "__main__":
    #main()
    main_circular()