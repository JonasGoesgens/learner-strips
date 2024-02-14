#predicates
#clear(x)
#on(x,y)

def compute_flag_pos(num_objects):
    curr_pos = 0
    clear_pos = curr_pos
    curr_pos += num_objects
    on_pos = curr_pos
    curr_pos += num_objects * num_objects
    return clear_pos, on_pos, curr_pos

def compute_num_nodes(num_objects):
    clear_pos, on_pos, curr_pos = compute_flag_pos(num_objects)
    return (1 << curr_pos)

#all_flags = num_nodes - 1
#encoding bittable: clear0,clear1,on00,on01,on10,on11

#actions: build flags
#unstack x,y
#Pre = onblock(x,y) wedge clear(x) wedge x != y
#Add = onblock(x,x) wedge clear(y)
#Del = onblock(x,y)
def compute_unstack_flags(num_objects):
    clear_pos, on_pos, curr_pos = compute_flag_pos(num_objects)
    unstack_action_flags = [[0] * 4 for i in range(num_objects * num_objects - num_objects)]
    index = 0
    for j in range(0, num_objects):
        for k in range(0, num_objects):
            if (k != j):
                pre = 0
                pre = pre | (1 << (clear_pos + j))
                pre = pre | (1 << (on_pos + j*num_objects + k))
                unstack_action_flags[index][0] = pre
                add = 0
                add = add | (1 << (on_pos + j*num_objects + j))
                add = add | (1 << (clear_pos + k))
                unstack_action_flags[index][1] = add
                dele = 0
                dele = dele | (1 << (on_pos + j*num_objects + k))
                unstack_action_flags[index][2] = dele
                unstack_action_flags[index][3] = [j,k]
                index += 1
    return unstack_action_flags

#stack x,y
#Pre = onblock(x,x) wedge clear(y) wedge clear(x) wedge x != y
#Add = onblock(x,y)
#Del = onblock(x,x) wedge clear(y)
def compute_stack_flags(num_objects):
    clear_pos, on_pos, curr_pos = compute_flag_pos(num_objects)
    stack_action_flags = [[0] * 4 for i in range(num_objects * num_objects - num_objects)]
    index = 0
    for j in range(0, num_objects):
        for k in range(0, num_objects):
            if (k != j):
                pre = 0
                pre = pre | (1 << (on_pos + j*num_objects + j))
                pre = pre | (1 << (clear_pos + j))
                pre = pre | (1 << (clear_pos + k))
                stack_action_flags[index][0] = pre
                add = 0
                add = add | (1 << (on_pos + j*num_objects + k))
                stack_action_flags[index][1] = add
                dele = 0
                dele = dele | (1 << (on_pos + j*num_objects + j))
                dele = dele | (1 << (clear_pos + k))
                stack_action_flags[index][2] = dele
                stack_action_flags[index][3] = [j,k]
                index += 1
    return stack_action_flags

#move x,y,z
#Pre = onblock(x,y) wedge clear(z) wedge clear(x) wedge x != y != z
#Add = onblock(x,z) wedge clear(y)
#Del = onblock(x,y) wedge clear(z)
def compute_move_flags(num_objects):
    clear_pos, on_pos, curr_pos = compute_flag_pos(num_objects)
    move_action_flags = [[0] * 4 for i in range(num_objects * (num_objects - 1 ) *(num_objects - 2))]
    index = 0
    for i in range(0, num_objects):
        for j in range(0, num_objects):
            for k in range(0, num_objects):
                if (i != j and i != k and k != j):
                    pre = 0
                    pre = pre | (1 << (on_pos + i*num_objects + j))
                    pre = pre | (1 << (clear_pos + i))
                    pre = pre | (1 << (clear_pos + k))
                    move_action_flags[index][0] = pre
                    add = 0
                    add = add | (1 << (on_pos + i*num_objects + k))
                    add = add | (1 << (clear_pos + j))
                    move_action_flags[index][1] = add
                    dele = 0
                    dele = dele | (1 << (on_pos + i*num_objects + j))
                    dele = dele | (1 << (clear_pos + k))
                    move_action_flags[index][2] = dele
                    move_action_flags[index][3] = [i,j,k]
                    index += 1
    return move_action_flags

def compute_init_nodes(num_objects):
    clear_pos, on_pos, curr_pos = compute_flag_pos(num_objects)
    initnode = 0
    for j in range(0, num_objects):
        initnode = initnode | (1 << (on_pos + j*num_objects + j))
        initnode = initnode | (1 << (clear_pos + j))
    return [initnode]

def get_action_names(i):
    names = ["NEWTOWER", "STACK", "MOVE"]
    return names[i]

for num_objects in range (2,4):
    unstack_action_flags = compute_unstack_flags(num_objects)
    stack_action_flags = compute_stack_flags(num_objects)
    move_action_flags = compute_move_flags(num_objects)
    num_nodes = compute_num_nodes(num_objects)
    output_string = ""
    for i in range(0, num_nodes):
        output_string += "node(" + str(i) + ").\n"
        #unstack x,y
        for flags in unstack_action_flags:
            if i & flags[0] == flags[0]:
                target = ((i | flags[1]) & ~flags[2])# & all_flags
                obj_string = ""
                skipfirst=False
                count=0
                for obj in flags[3]:
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
                output_string += "tlabel(( " + str(i) + ", " + str(target) + "), " +str(0+1) + ",(" + obj_string + ")).\n"
                output_string += "edge(( " + str(i) + ", " + str(target) + ")).\n"
        
        #stack x,y
        for flags in stack_action_flags:
            if i & flags[0] == flags[0]:
                target = ((i | flags[1]) & ~flags[2])# & all_flags
                obj_string = ""
                skipfirst=False
                count=0
                for obj in flags[3]:
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
                output_string += "tlabel(( " + str(i) + ", " + str(target) + "), " +str(1+1) + ",(" + obj_string + ")).\n"
                output_string += "edge(( " + str(i) + ", " + str(target) + ")).\n"
        
        #move x,y,z
        for flags in move_action_flags:
            if i & flags[0] == flags[0]:
                target = ((i | flags[1]) & ~flags[2])# & all_flags
                obj_string = ""
                skipfirst=False
                count=0
                for obj in flags[3]:
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
                output_string += "tlabel(( " + str(i) + ", " + str(target) + "), " +str(2+1) + ",(" + obj_string + ")).\n"
                output_string += "edge(( " + str(i) + ", " + str(target) + ")).\n"
    output_string = "labelname("+str(0+1)+",\""+get_action_names(0)+"\").\n" + "labelname("+str(1+1)+",\""+get_action_names(1)+"\").\n" + "labelname("+str(2+1)+",\""+get_action_names(2)+"\").\n" + output_string
    filename = "blocks3ops_" + str(num_objects) + "_no_constraints_full_label.lp"
    with open(filename, 'w') as f:
        f.write(output_string)

for num_objects in range (2,6):
    unstack_action_flags = compute_unstack_flags(num_objects)
    stack_action_flags = compute_stack_flags(num_objects)
    move_action_flags = compute_move_flags(num_objects)
    
    node_id = 0
    output_nodes = []
    output_edges = []
    output_connections = []
    num_nodes = 0
    todo_nodes = compute_init_nodes(num_objects)
    #build nodes
    while todo_nodes:
        current_node = todo_nodes.pop(0)
        output_nodes.append(current_node)
        num_nodes += 1
        current_edges = []
        connections = 0
        #unstack x,y
        for flags in unstack_action_flags:
                if current_node & flags[0] == flags[0]:
                    connections += 1
                    target = ((current_node | flags[1]) & ~flags[2])# & all_flags
                    if not ((target in output_nodes) or (target in todo_nodes)):
                        todo_nodes.append(target)
                    current_edges.append([0,target,flags[3]])
        
        #stack x,y
        for flags in stack_action_flags:
                if current_node & flags[0] == flags[0]:
                    connections += 1
                    target = ((current_node | flags[1]) & ~flags[2])# & all_flags
                    if not ((target in output_nodes) or (target in todo_nodes)):
                        todo_nodes.append(target)
                    current_edges.append([1,target,flags[3]])
        
        #move x,y,z
        for flags in move_action_flags:
                if current_node & flags[0] == flags[0]:
                    connections += 1
                    target = ((current_node | flags[1]) & ~flags[2])# & all_flags
                    if not ((target in output_nodes) or (target in todo_nodes)):
                        todo_nodes.append(target)
                    current_edges.append([2,target,flags[3]])
        
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
    output_string = "dfa " + str(num_nodes) + " -1\n" + "3 "+get_action_names(0)+" "+get_action_names(1)+" "+get_action_names(2)+"\n" + "1 0\n" + output_string
    filename = "blocks3ops_" + str(num_objects) + "_full_label.dfa"
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
    output_string = "labelname("+str(0+1)+",\""+get_action_names(0)+"\").\n" + "labelname("+str(1+1)+",\""+get_action_names(1)+"\").\n" + "labelname("+str(2+1)+",\""+get_action_names(2)+"\").\n" + output_string
    filename = "blocks3ops_" + str(num_objects) + "_full_label.lp"
    with open(filename, 'w') as f:
        f.write(output_string)
