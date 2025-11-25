#main
import Node
import time
import host
import client

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
        node = Node.node(name=f"test_node_{i}",val=nums[i])
        nodes.append(node)
        node.produce()
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

def main_distributed():
    #distributed test with host and clients
    print("host or client?")
    ans=str(input())
    if ans=="host":
        vals=[]#node values
        host1 = host.Host()
        print("how many clients for testing?")
        num_hosts = int(input())
        print("how many nodes for testing?")
        num_nodes = int(input())
        for node in range(num_nodes):
            print(f"Enter value for node {node}:")
            vals.append(int(input()))
        host1.start(total_nodes=num_nodes,max_clients=num_hosts, node_vals=vals)
        return
    if ans=="client":
        client_id=input("Enter client ID:")
        #host_ip=input("Enter host IP (default localhost):")
        client1 = client.Client(client_id=client_id)
        client1.run()
        return
    
if __name__ == "__main__":
    #main()
    #main_circular()
    main_distributed()