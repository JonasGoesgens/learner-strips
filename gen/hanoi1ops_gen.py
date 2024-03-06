#predicates
#p(x,y)

def compute_flag_pos(num_objects):
    curr_pos = 0
    p_pos = curr_pos
    curr_pos += num_objects * num_objects
    return p_pos, curr_pos

def compute_num_nodes(num_objects):
    p_pos, curr_pos = compute_flag_pos(num_objects)
    return (1 << curr_pos)

#all_flags = num_nodes - 1
#encoding bittable: p00,p01,p10,p11

#actions: build flags
#move x,y,z
#Pre = p(x,x) wedge p(z,z) wedge p(x,y) wedge p(y,x) wedge p(x,z) wedge x != y != z != x
#Add = p(z,x) wedge p(y,y)
#Del = p(y,x) wedge p(z,z)
def compute_move_flags(num_objects):
    p_pos, curr_pos = compute_flag_pos(num_objects)
    move_action_flags = [[0] * 4 for i in range(num_objects * (num_objects - 1 ) *(num_objects - 2))]
    index = 0
    for i in range(0, num_objects):
        for j in range(0, num_objects):
            for k in range(0, num_objects):
                if (i != j and i != k and k != j):
                    pre = 0
                    pre = pre | (1 << (p_pos + i*num_objects + i))
                    pre = pre | (1 << (p_pos + k*num_objects + k))
                    pre = pre | (1 << (p_pos + i*num_objects + j))
                    pre = pre | (1 << (p_pos + j*num_objects + i))
                    pre = pre | (1 << (p_pos + i*num_objects + k))
                    move_action_flags[index][0] = pre
                    add = 0
                    add = add | (1 << (p_pos + k*num_objects + i))
                    add = add | (1 << (p_pos + j*num_objects + j))
                    move_action_flags[index][1] = add
                    dele = 0
                    dele = dele | (1 << (p_pos + j*num_objects + i))
                    dele = dele | (1 << (p_pos + k*num_objects + k))
                    move_action_flags[index][2] = dele
                    move_action_flags[index][3] = [i,j,k]
                    index += 1
    return move_action_flags

def compute_init_nodes(num_objects, num_pillars):
    assert(num_pillars < num_objects)
    p_pos, curr_pos = compute_flag_pos(num_objects)
    initnode = 0
    for i in range(0, num_objects):
        for j in range(0, num_objects):
            if   (i < j and j >= num_pillars):                                           #static one area
                initnode = initnode | (1 << (p_pos + j*num_objects + i))
    for i in range(num_pillars, num_objects):                                            #discs on last pillar stacked
        initnode = initnode | (1 << (p_pos + (i-1)*num_objects + (i)))
    for i in range(0, num_pillars -1):                                                   #clear pillars
        initnode = initnode | (1 << (p_pos + i*num_objects + i))
    initnode = initnode | (1 << (p_pos + (num_objects-1)*num_objects + (num_objects-1))) #clear disk
    print("initnode_" + str(num_pillars) + "x" + str(num_objects-num_pillars) + ": " + str(initnode) + "\n")
    return [initnode]

def get_action_names(i):
    names = ["MOVE"]
    return names[i]

for num_pillars in range (3,5):
    for num_objects in range (5,9):
        move_action_flags = compute_move_flags(num_objects)
        
        node_id = 0
        output_nodes = []
        output_edges = []
        output_connections = []
        num_nodes = 0
        todo_nodes = compute_init_nodes(num_objects, num_pillars)
        #build nodes
        while todo_nodes:
            current_node = todo_nodes.pop(0)
            output_nodes.append(current_node)
            num_nodes += 1
            current_edges = []
            connections = 0
            #move x,y,z
            for flags in move_action_flags:
                if current_node & flags[0] == flags[0]:
                    connections += 1
                    target = ((current_node | flags[1]) & ~flags[2])# & all_flags
                    if not ((target in output_nodes) or (target in todo_nodes)):
                        todo_nodes.append(target)
                    current_edges.append([0,target,flags[3]])
            
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
                obj_string=""
                skipfirst=False
                for obj in labeled_edge[2]:
                    if skipfirst:
                        obj_string += " "
                    skipfirst=True
                    obj_string += str(obj)
                node_string += " " + get_action_names(labeled_edge[0]) + "[" + obj_string + "] " + str(index)
            output_string += str(connections) + node_string + "\n"
        output_string = "dfa " + str(num_nodes) + " -1\n" + "1 "+get_action_names(0)+"\n" + "1 0\n" + output_string
        filename = "hanoi1op_" + str(num_pillars) + "x" + str(num_objects-num_pillars) + "_full_label.dfa"
        with open(filename, 'w') as f:
            f.write(output_string)

        #build string
        output_string = ""
        for i,node in enumerate(output_nodes):
            output_string += "node(" + str(i) + ").\n"
            current_edges = output_edges[i]
            connections = output_connections[i]
            for labeled_edge in current_edges:
                index = output_nodes.index(labeled_edge[1])
                obj_string=""
                skipfirst=False
                count=0
                for obj in labeled_edge[2]:
                    count+=1
                    if skipfirst:
                        obj_string += ", "
                    skipfirst=True
                    obj_string += str(obj)
                while count < 3:
                    count+=1
                    if skipfirst:
                        obj_string += ", "
                    skipfirst=True
                    obj_string += str(-1)
                output_string += "tlabel(( " + str(i) + ", " + str(index) + "), " +str(labeled_edge[0]+1) + ",(" + obj_string + ")).\n"
                output_string += "edge(( " + str(i) + ", " + str(index) + ")).\n"
        output_string = "labelname("+str(0+1)+",\""+get_action_names(0)+"\").\n" + output_string
        filename = "hanoi1op_" + str(num_pillars) + "x" + str(num_objects-num_pillars) + "_full_label.lp"
        with open(filename, 'w') as f:
            f.write(output_string)
