#predicates
#connected(x,y)

def compute_flag_pos(num_objects):
    curr_pos = 0
    connected_pos = curr_pos
    curr_pos += num_objects * num_objects
    return connected_pos, curr_pos

def compute_num_nodes(num_objects):
    connected_pos, curr_pos = compute_flag_pos(num_objects)
    return (1 << curr_pos)

#all_flags = num_nodes - 1
#encoding bittable: clear0,clear1,on00,on01,on10,on11

#actions: build flags
#move x,y
#Pre = connected(x,y) wedge connected(x,x) wedge x != y
#Add = connected(y,y)
#Del = connected(x,x)
def compute_move_flags(num_objects):
    connected_pos, curr_pos = compute_flag_pos(num_objects)
    move_action_flags = [[0] * 3 for i in range(num_objects * num_objects - num_objects)]
    index = 0
    for j in range(0, num_objects):
        for k in range(0, num_objects):
            if (k != j):
                pre = 0
                pre = pre | (1 << (connected_pos + j*num_objects + j))
                pre = pre | (1 << (connected_pos + j*num_objects + k))
                move_action_flags[index][0] = pre
                add = 0
                add = add | (1 << (connected_pos + k*num_objects + k))
                move_action_flags[index][1] = add
                dele = 0
                dele = dele | (1 << (connected_pos + j*num_objects + j))
                move_action_flags[index][2] = dele
                index += 1
    return move_action_flags

def compute_init_nodes(num_objects, pattern):
    connected_pos, curr_pos = compute_flag_pos(num_objects)
    graph = (pow(13,pattern) + pattern*pattern) % pow(2,num_objects*num_objects)
    diagdelete = 0
    for j in range(0, num_objects):
        for k in range(0, num_objects):
            if (k != j):
                diagdelete = diagdelete | (1 << (j*num_objects + k))
    graph = graph & diagdelete
    initnodes = []
    #print("\nGraph: " + "{0:#08b}".format(graph))
    for j in range(0, num_objects):
        initnodes.append((graph << connected_pos) | (1 << (connected_pos + j*num_objects + j)))
    #for initnode in initnodes:
    #    print("{0:#08b}".format(initnode))
    return initnodes
for num_objects in [2,3]:
    move_action_flags = compute_move_flags(num_objects)

    num_nodes = compute_num_nodes(num_objects)
    output_string = ""
    dot_output_string = ""
    #build nodes
    for i in range(0, num_nodes):
        connections = 0
        node_string = ""
        dot_node_string = "N" + "{0:#06b}".format(i)
        #move x,y
        b_edge = False
        for flags in move_action_flags:
            if (i & flags[0]) == flags[0]:
                connections += 1
                target = ((i | flags[1]) & ~flags[2])# & all_flags
                node_string += " move " + str(target)
                if not b_edge:
                    dot_node_string += " -> { "
                    b_edge = True
                dot_node_string += "N" + "{0:#06b}".format(target) + " " 
        if b_edge:
            dot_node_string += "}"
        output_string += str(connections) + node_string + "\n"
        dot_output_string += dot_node_string + "\n"
    dot_output_string = "digraph { \n" + dot_output_string + "}"
    output_string = "dfa " + str(num_nodes) + " -1\n" + "1 move\n" + "1 0\n" + output_string
    with open('navgraphmin1ops' + str(num_objects) + '_noconstraints.dfa', 'w') as f:
        f.write(output_string)

    with open('navgraphmin1ops' + str(num_objects) + '_noconstraints.dot', 'w') as f:
        f.write(dot_output_string)


for num_objects in range (2,9):
    for pattern in [73,26,57,48]:
        move_action_flags = compute_move_flags(num_objects)

        node_id = 0
        output_nodes = []
        output_edges = []
        output_connections = []
        num_nodes = 0
        todo_nodes = compute_init_nodes(num_objects,pattern)
        #build nodes
        while todo_nodes:
            current_node = todo_nodes.pop(0)
            output_nodes.append(current_node)
            num_nodes += 1
            current_edges = []
            connections = 0
            #move x,y
            for flags in move_action_flags:
                    if current_node & flags[0] == flags[0]:
                        connections += 1
                        target = ((current_node | flags[1]) & ~flags[2])# & all_flags
                        if not ((target in output_nodes) or (target in todo_nodes)):
                            todo_nodes.append(target)
                        current_edges.append([" move ",target])

            output_edges.append(current_edges)
            output_connections.append(connections)

        #build string
        output_string = ""
        for i,node in enumerate(output_nodes):
            current_edges = output_edges[i]
            connections = output_connections[i]
            node_string = ""
            for labeled_edge in current_edges:
                index = output_nodes.index(labeled_edge[1])
                node_string += labeled_edge[0] + str(index)
            output_string += str(connections) + node_string + "\n"
        output_string = "dfa " + str(num_nodes) + " -1\n" + "1 move\n" + "1 0\n" + output_string
        filename = "navgraphmin1ops" + str(num_objects) + "pat" + str(pattern) + ".dfa"
        with open(filename, 'w') as f:
            f.write(output_string)
