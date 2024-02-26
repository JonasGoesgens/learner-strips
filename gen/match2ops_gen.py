#predicates
#clear(x)
#on(x,y)

def compute_flag_pos(num_objects):
    curr_pos = 0
    matched_pos = curr_pos
    curr_pos += num_objects * num_objects
    return matched_pos, curr_pos

def compute_num_nodes(num_objects):
    matched_pos, curr_pos = compute_flag_pos(num_objects)
    return (1 << curr_pos)

#all_flags = num_nodes - 1
#encoding bittable: clear0,clear1,on00,on01,on10,on11

#actions: build flags
#unmatch x,y
#Pre = matched(x,y) wedge matched(y,x) wedge x != y
#Add = matched(x,x) wedge matched(y,y)
#Del = matched(x,y) wedge matched(y,x)
def compute_unmatch_flags(num_objects):
    matched_pos, curr_pos = compute_flag_pos(num_objects)
    unmatch_action_flags = [[0] * 4 for i in range(num_objects * num_objects - num_objects)]
    index = 0
    for j in range(0, num_objects):
        for k in range(0, num_objects):
            if (k != j):
                pre = 0
                pre = pre | (1 << (matched_pos + j*num_objects + k))
                pre = pre | (1 << (matched_pos + k*num_objects + j))
                unmatch_action_flags[index][0] = pre
                add = 0
                add = add | (1 << (matched_pos + j*num_objects + j))
                add = add | (1 << (matched_pos + k*num_objects + k))
                unmatch_action_flags[index][1] = add
                dele = 0
                dele = dele | (1 << (matched_pos + j*num_objects + k))
                dele = dele | (1 << (matched_pos + k*num_objects + j))
                unmatch_action_flags[index][2] = dele
                unmatch_action_flags[index][3] = [j,k]
                index += 1
    return unmatch_action_flags

#match x,y
#Pre = matched(x,x) wedge matched(y,y) wedge x != y
#Add = matched(x,y) wedge matched(y,x)
#Del = matched(x,x) wedge matched(y,y)
def compute_match_flags(num_objects):
    matched_pos, curr_pos = compute_flag_pos(num_objects)
    match_action_flags = [[0] * 4 for i in range(num_objects * num_objects - num_objects)]
    index = 0
    for j in range(0, num_objects):
        for k in range(0, num_objects):
            if (k != j):
                pre = 0
                pre = pre | (1 << (matched_pos + j*num_objects + j))
                pre = pre | (1 << (matched_pos + k*num_objects + k))
                match_action_flags[index][0] = pre
                add = 0
                add = add | (1 << (matched_pos + j*num_objects + k))
                add = add | (1 << (matched_pos + k*num_objects + j))
                match_action_flags[index][1] = add
                dele = 0
                dele = dele | (1 << (matched_pos + j*num_objects + j))
                dele = dele | (1 << (matched_pos + k*num_objects + k))
                match_action_flags[index][2] = dele
                match_action_flags[index][3] = [j,k]
                index += 1
    return match_action_flags

def compute_init_nodes(num_objects):
    matched_pos, curr_pos = compute_flag_pos(num_objects)
    initnode = 0
    for j in range(0, num_objects):
        initnode = initnode | (1 << (matched_pos + j*num_objects + j))
    return [initnode]

def get_action_names(i):
    names = ["UNMATCH", "MATCH"]
    return names[i]

for num_objects in range (2,4):
    unmatch_action_flags = compute_unmatch_flags(num_objects)
    match_action_flags = compute_match_flags(num_objects)
    num_nodes = compute_num_nodes(num_objects)
    output_string = ""
    for i in range(0, num_nodes):
        output_string += "node(" + str(i) + ").\n"
        #unmatch x,y
        for flags in unmatch_action_flags:
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
        
        #match x,y
        for flags in match_action_flags:
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
        
    output_string = "labelname("+str(0+1)+",\""+get_action_names(0)+"\").\n" + "labelname("+str(1+1)+",\""+get_action_names(1)+"\").\n" + output_string
    filename = "blocks3ops_" + str(num_objects) + "_no_constraints_full_label.lp"
    with open(filename, 'w') as f:
        f.write(output_string)

for num_objects in range (2,6):
    unmatch_action_flags = compute_unmatch_flags(num_objects)
    match_action_flags = compute_match_flags(num_objects)
    
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
        #unmatch x,y
        for flags in unmatch_action_flags:
                if current_node & flags[0] == flags[0]:
                    connections += 1
                    target = ((current_node | flags[1]) & ~flags[2])# & all_flags
                    if not ((target in output_nodes) or (target in todo_nodes)):
                        todo_nodes.append(target)
                    current_edges.append([0,target,flags[3]])
        
        #match x,y
        for flags in match_action_flags:
                if current_node & flags[0] == flags[0]:
                    connections += 1
                    target = ((current_node | flags[1]) & ~flags[2])# & all_flags
                    if not ((target in output_nodes) or (target in todo_nodes)):
                        todo_nodes.append(target)
                    current_edges.append([1,target,flags[3]])
        
        output_edges.append(current_edges)
        output_connections.append(connections)
    
    #build string
    output_string = ""
    full_output_string = ""
    for i,node in enumerate(output_nodes):
        current_edges = output_edges[i]
        connections = output_connections[i]
        node_string = ""
        full_node_string = ""
        for labeled_edge in current_edges:
            index = output_nodes.index(labeled_edge[1])
            obj_string=""
            skipfirst=False
            for obj in labeled_edge[2]:
                if skipfirst:
                    obj_string += " "
                skipfirst=True
                obj_string += str(obj)
            node_string += " " + get_action_names(labeled_edge[0])+ " " + str(index)
            full_node_string += " " + get_action_names(labeled_edge[0]) + "[" + obj_string + "] " + str(index)
        output_string += str(connections) + node_string + "\n"
        full_output_string += str(connections) + full_node_string + "\n"
    output_string = "dfa " + str(num_nodes) + " -1\n" + "2 "+get_action_names(0)+" "+get_action_names(1)+"\n" + "1 0\n" + output_string
    full_output_string = "dfa " + str(num_nodes) + " -1\n" + "2 "+get_action_names(0)+" "+get_action_names(1)+"\n" + "1 0\n" + full_output_string
    filename = "match2ops_" + str(num_objects) + ".dfa"
    with open(filename, 'w') as f:
        f.write(output_string)
    filename = "match2ops_" + str(num_objects) + "_full_label.dfa"
    with open(filename, 'w') as f:
        f.write(full_output_string)

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
    output_string = "labelname("+str(0+1)+",\""+get_action_names(0)+"\").\n" + "labelname("+str(1+1)+",\""+get_action_names(1)+"\").\n" + output_string
    filename = "match2ops_" + str(num_objects) + "_full_label.lp"
    with open(filename, 'w') as f:
        f.write(output_string)
