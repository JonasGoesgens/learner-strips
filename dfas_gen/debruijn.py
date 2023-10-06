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

for num_objects in range(2,8):
    output_string = ""
    num_nodes = (1 << num_objects)
    for node in range(0,num_nodes):
        node_string = ""
        target = node
        target = ((target << 1) | (target >> num_objects - 1)) % num_nodes
        node_string += " shuffle " + str(target)
        target = (node & ~1) | (~node & 1)
        target = ((target << 1) | (target >> num_objects - 1)) % num_nodes
        node_string += " shuffleexchange " + str(target)
        output_string += str(2) + node_string + "\n"
    output_string = "dfa " + str(num_nodes) + " -1\n" + "2 shuffle shuffleexchange\n" + "1 0\n" + output_string
    with open('debruijn' + str(num_objects) + '.dfa', 'w') as f:
        f.write(output_string)
