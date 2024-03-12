#predicates
#connected(x,y)
#bit(x)
#actions
#shuffle(x,y)
#connected(x,x),connected(x,y)
#connected(y,y)
#connected(x,x)
#shuffleexchange(x,y)
#connected(x,x),connected(x,y)
#not bit(x), connected(y,y)
#bit(x), connected(x,x)

# tlabel(( 0, 1), 2,(0, 1, -1)). 
# edge 
# node 
# labelname : shuffle, shuffleexchange 

for num_objects in range(2,4):
    output_string = "labelname(1,\"shuffle\").\n" + "labelname(2,\"shuffleexchange0\").\n" + "labelname(3,\"shuffleexchange1\").\n"
    num_nodes = (1 << num_objects)
    for phase in range(0,num_objects):
        for node in range(0,num_nodes):
            state = node | (((phase) % num_objects ) << num_objects)
            node_string = "node("+str(state)+").\n"
            target = node
            target = ((target << 1) | (target >> num_objects - 1)) % num_nodes
            target = target | (((phase + 1) % num_objects ) << num_objects)
            node_string += "edge((" + str(state) + "," + str(target) + ")).\n"
            node_string += "tlabel((" + str(state) + "," + str(target) + "),1,("+str(phase) + "," +str((phase+1)%num_objects) +",-1)).\n"
            target = (node & ~1) | (~node & 1)
            target = ((target << 1) | (target >> num_objects - 1)) % num_nodes
            target = target | (((phase + 1) % num_objects ) << num_objects)
            node_string += "edge((" + str(state) + "," + str(target) + ")).\n"
            node_string += "tlabel((" + str(state) + "," + str(target) + "),"+str(2+(node & 1))+",("+str(phase) + "," +str((phase+1)%num_objects) +",-1)).\n"
            output_string += node_string
    with open('storagering3ops_' + str(num_objects) + '_full_label.lp', 'w') as f:
        f.write(output_string)
