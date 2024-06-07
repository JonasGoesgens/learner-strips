#predicates
#clear(x)
#on(x,y)

def compute_flag_pos(num_objects):
    curr_pos = 0
    clear_pos = curr_pos
    curr_pos += num_objects
    ontable_pos = curr_pos
    curr_pos += num_objects
    on_pos = curr_pos
    curr_pos += num_objects * num_objects
    grabbed_pos = curr_pos
    curr_pos += num_objects
    empty_pos = curr_pos
    curr_pos += 1
    return clear_pos, ontable_pos, on_pos, grabbed_pos, empty_pos, curr_pos

def compute_num_nodes(num_objects):
    clear_pos, ontable_pos, on_pos, grabbed_pos, empty_pos, curr_pos = compute_flag_pos(num_objects)
    return (1 << curr_pos)

#all_flags = num_nodes - 1
#encoding bittable: clear0,clear1,on00,on01,on10,on11

#actions: build flags
#unstack x,y
#Pre = onblock(x,y) wedge clear(x) wedge empty wedge x != y
#Add = grabbed(x)   wedge clear(y)
#Del = onblock(x,y) wedge clear(x) wedge empty
def compute_unstack_flags(num_objects):
    clear_pos, ontable_pos, on_pos, grabbed_pos, empty_pos, curr_pos = compute_flag_pos(num_objects)
    unstack_action_flags = [[0] * 4 for i in range(num_objects * num_objects - num_objects)]
    index = 0
    for j in range(0, num_objects):
        for k in range(0, num_objects):
            if (k != j):
                pre = 0
                pre = pre | (1 << (clear_pos + j))
                pre = pre | (1 << (on_pos + j*num_objects + k))
                pre = pre | (1 << (empty_pos))
                unstack_action_flags[index][0] = pre
                add = 0
                add = add | (1 << (grabbed_pos + j))
                add = add | (1 << (clear_pos + k))
                unstack_action_flags[index][1] = add
                dele = 0
                dele = dele | (1 << (on_pos + j*num_objects + k))
                dele = dele | (1 << (empty_pos))
                dele = dele | (1 << (clear_pos + j))
                unstack_action_flags[index][2] = dele
                unstack_action_flags[index][3] = [j,k]
                index += 1
    return unstack_action_flags

#stack x,y
#Pre = grabbed(x)   wedge clear(y) wedge x != y
#Add = onblock(x,y) wedge clear(x) wedge empty
#Del = grabbed(x)   wedge clear(y)
def compute_stack_flags(num_objects):
    clear_pos, ontable_pos, on_pos, grabbed_pos, empty_pos, curr_pos = compute_flag_pos(num_objects)
    stack_action_flags = [[0] * 4 for i in range(num_objects * num_objects - num_objects)]
    index = 0
    for j in range(0, num_objects):
        for k in range(0, num_objects):
            if (k != j):
                pre = 0
                pre = pre | (1 << (grabbed_pos + j))
                pre = pre | (1 << (clear_pos + k))
                stack_action_flags[index][0] = pre
                add = 0
                add = add | (1 << (on_pos + j*num_objects + k))
                add = add | (1 << (empty_pos))
                add = add | (1 << (clear_pos + j))
                stack_action_flags[index][1] = add
                dele = 0
                dele = dele | (1 << (grabbed_pos + j))
                dele = dele | (1 << (clear_pos + k))
                stack_action_flags[index][2] = dele
                stack_action_flags[index][3] = [j,k]
                index += 1
    return stack_action_flags

#pick x
#Pre = ontable(x) wedge clear(x) wedge empty
#Add = grabbed(x)
#Del = ontable(x) wedge clear(x) wedge empty
def compute_pick_flags(num_objects):
    clear_pos, ontable_pos, on_pos, grabbed_pos, empty_pos, curr_pos = compute_flag_pos(num_objects)
    pick_action_flags = [[0] * 4 for i in range(num_objects)]
    index = 0
    for j in range(0, num_objects):
        pre = 0
        pre = pre | (1 << (clear_pos + j))
        pre = pre | (1 << (ontable_pos + j))
        pre = pre | (1 << (empty_pos))
        pick_action_flags[index][0] = pre
        add = 0
        add = add | (1 << (grabbed_pos + j))
        pick_action_flags[index][1] = add
        dele = 0
        dele = dele | (1 << (ontable_pos + j))
        dele = dele | (1 << (empty_pos))
        dele = dele | (1 << (clear_pos + j))
        pick_action_flags[index][2] = dele
        pick_action_flags[index][3] = [j]
        index += 1
    return pick_action_flags

#put x
#Pre = grabbed(x)
#Add = ontable(x) wedge clear(x) wedge empty
#Del = grabbed(x)
def compute_put_flags(num_objects):
    clear_pos, ontable_pos, on_pos, grabbed_pos, empty_pos, curr_pos = compute_flag_pos(num_objects)
    put_action_flags = [[0] * 4 for i in range(num_objects)]
    index = 0
    for j in range(0, num_objects):
        pre = 0
        pre = pre | (1 << (grabbed_pos + j))
        put_action_flags[index][0] = pre
        add = 0
        add = add | (1 << (ontable_pos + j))
        add = add | (1 << (empty_pos))
        add = add | (1 << (clear_pos + j))
        put_action_flags[index][1] = add
        dele = 0
        dele = dele | (1 << (grabbed_pos + j))
        put_action_flags[index][2] = dele
        put_action_flags[index][3] = [j]
        index += 1
    return put_action_flags

def compute_init_nodes(num_objects):
    clear_pos, ontable_pos, on_pos, grabbed_pos, empty_pos, curr_pos = compute_flag_pos(num_objects)
    initnode = 0
    initnode = initnode | (1 << (empty_pos))
    for j in range(0,int(num_objects/2)-1):
        initnode = initnode | (1 << (on_pos + (j+1)*num_objects + j))
    for j in range(int(num_objects/2),num_objects-1):
        initnode = initnode | (1 << (on_pos + (j+1)*num_objects + j))
    for j in [int(num_objects/2)-1,num_objects-1]:
        initnode = initnode | (1 << (clear_pos + j))
    for j in [0,int(num_objects/2)]:
        initnode = initnode | (1 << (ontable_pos + j))
    return [initnode]

def get_action_names(i):
    names = ["UNSTACK", "STACK", "PICK", "PUT"]
    return names[i]

for num_objects in [4,6]:
    unstack_action_flags = compute_unstack_flags(num_objects)
    stack_action_flags = compute_stack_flags(num_objects)
    pick_action_flags = compute_pick_flags(num_objects)
    put_action_flags = compute_put_flags(num_objects)
    
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
        
        #pick x
        for flags in pick_action_flags:
                if current_node & flags[0] == flags[0]:
                    connections += 1
                    target = ((current_node | flags[1]) & ~flags[2])# & all_flags
                    if not ((target in output_nodes) or (target in todo_nodes)):
                        todo_nodes.append(target)
                    current_edges.append([2,target,flags[3]])
        
        #piputck x
        for flags in put_action_flags:
                if current_node & flags[0] == flags[0]:
                    connections += 1
                    target = ((current_node | flags[1]) & ~flags[2])# & all_flags
                    if not ((target in output_nodes) or (target in todo_nodes)):
                        todo_nodes.append(target)
                    current_edges.append([3,target,flags[3]])
        
        output_edges.append(current_edges)
        output_connections.append(connections)

    #build string
    output_string = ""
    for i,node in enumerate(output_nodes):
        output_string += "node(" + str(i) + ").\n"
        clear_pos, ontable_pos, on_pos, grabbed_pos, empty_pos, curr_pos = compute_flag_pos(num_objects)
        if (node & (1 << (empty_pos))):
            output_string += "val(" + str(i) + ", 5, (-1, -1), 1).\n"
        for j in range(0, num_objects):
            if (node & (1 << (ontable_pos + j))):
                output_string += "val(" + str(i) + ", 2, (" + str(j+1) + ", -1), 1).\n"
            if (node & (1 << (clear_pos + j))):
                output_string += "val(" + str(i) + ", 3, (" + str(j+1) + ", -1), 1).\n"
            if (node & (1 << (grabbed_pos + j))):
                output_string += "val(" + str(i) + ", 4, (" + str(j+1) + ", -1), 1).\n"
            for k in range(0, num_objects):
                if (node & (1 << (on_pos + j*num_objects + k))):
                    output_string += "val(" + str(i) + ", 1, (" + str(j+1) + ", " + str(k+1) + "), 1).\n"
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
                obj_string += str(obj+1)
            while count < 2:
                count+=1
                if skipfirst:
                    obj_string += ", "
                skipfirst=True
                obj_string += str(-1)
            output_string += "next( "+ str(labeled_edge[0]+1) + ",(" + obj_string + "), " + str(i)  + ", " + str(index) + ").\n"
    output_string = "labelname("+str(0+1)+",\""+get_action_names(0)+"\").\n" + "labelname("+str(1+1)+",\""+get_action_names(1)+"\").\n" + "labelname("+str(2+1)+",\""+get_action_names(2)+"\").\n" + "labelname("+str(3+1)+",\""+get_action_names(3)+"\").\n" + output_string
    filename = "blocks4ops_" + str(num_objects) + "_full_info.lp"
    with open(filename, 'w') as f:
        f.write(output_string)
