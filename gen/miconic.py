#predicates
#person(x)
#floor(x)
#lift_pos(x)
#in_lift(x)
#in_floor(x,y)
#above(x,y)

def compute_flag_pos(num_objects):
    curr_pos = 0
    person_pos = curr_pos
    curr_pos += num_objects
    floor_pos = curr_pos
    curr_pos += num_objects
    lift_pos = curr_pos
    curr_pos += num_objects
    in_lift_pos = curr_pos
    curr_pos += num_objects
    in_floor_pos = curr_pos
    curr_pos += num_objects * num_objects
    above_pos = curr_pos
    curr_pos += num_objects * num_objects
    return person_pos, floor_pos, lift_pos, in_lift_pos, in_floor_pos, above_pos, curr_pos

def compute_num_nodes(num_objects):
    clear_pos, on_pos, curr_pos = compute_flag_pos(num_objects)
    return (1 << curr_pos)

#all_flags = num_nodes - 1

#actions: build flags
#unboard x,y
#Pre = person(x) wedge floor(y) wedge lift_pos(y) wedge in_lift(x) wedge x != y
#Add = in_floor(x,y)
#Del = in_lift(x)
def compute_unboard_flags(num_objects):
    person_pos, floor_pos, lift_pos, in_lift_pos, in_floor_pos, above_pos, curr_pos = compute_flag_pos(num_objects)
    unboard_action_flags = [[0] * 4 for i in range(num_objects * num_objects - num_objects)]
    index = 0
    for j in range(0, num_objects):
        for k in range(0, num_objects):
            if (k != j):
                pre = 0
                pre = pre | (1 << (person_pos + j))
                pre = pre | (1 << (floor_pos + k))
                pre = pre | (1 << (lift_pos + k))
                pre = pre | (1 << (in_lift_pos + j))
                unboard_action_flags[index][0] = pre
                add = 0
                add = add | (1 << (in_floor_pos + j*num_objects + k))
                unboard_action_flags[index][1] = add
                dele = 0
                dele = dele | (1 << (in_lift_pos + j))
                unboard_action_flags[index][2] = dele
                unboard_action_flags[index][3] = [j,k]
                index += 1
    return unboard_action_flags

#board x,y
#Pre = person(x) wedge floor(y) wedge lift_pos(y) wedge in_floor(x,y) wedge x != y
#Add = in_lift(x)
#Del = in_floor(x,y)
def compute_board_flags(num_objects):
    person_pos, floor_pos, lift_pos, in_lift_pos, in_floor_pos, above_pos, curr_pos = compute_flag_pos(num_objects)
    board_action_flags = [[0] * 4 for i in range(num_objects * num_objects - num_objects)]
    index = 0
    for j in range(0, num_objects):
        for k in range(0, num_objects):
            if (k != j):
                pre = 0
                pre = pre | (1 << (person_pos + j))
                pre = pre | (1 << (floor_pos + k))
                pre = pre | (1 << (lift_pos + k))
                pre = pre | (1 << (in_floor_pos + j*num_objects + k))
                board_action_flags[index][0] = pre
                add = 0
                add = add | (1 << (in_lift_pos + j))
                board_action_flags[index][1] = add
                dele = 0
                dele = dele | (1 << (in_floor_pos + j*num_objects + k))
                board_action_flags[index][2] = dele
                board_action_flags[index][3] = [j,k]
                index += 1
    return board_action_flags

#move_up x,y,z
#Pre = floor(x) wedge floor(y) wedge lift_pos(x) wedge above(y,x) wedge x != y
#Add = lift_pos(y)
#Del = lift_pos(x)
def compute_move_up_flags(num_objects):
    person_pos, floor_pos, lift_pos, in_lift_pos, in_floor_pos, above_pos, curr_pos = compute_flag_pos(num_objects)
    move_up_action_flags = [[0] * 4 for i in range(num_objects * num_objects - num_objects)]
    index = 0
    for j in range(0, num_objects):
        for k in range(0, num_objects):
            if (k != j):
                pre = 0
                pre = pre | (1 << (floor_pos + j))
                pre = pre | (1 << (floor_pos + k))
                pre = pre | (1 << (lift_pos + j))
                pre = pre | (1 << (above_pos + k*num_objects + j))
                move_up_action_flags[index][0] = pre
                add = 0
                add = add | (1 << (lift_pos + k))
                move_up_action_flags[index][1] = add
                dele = 0
                dele = dele | (1 << (lift_pos + j))
                move_up_action_flags[index][2] = dele
                move_up_action_flags[index][3] = [j,k]
                index += 1
    return move_up_action_flags

#move_down x,y,z
#Pre = floor(x) wedge floor(y) wedge lift_pos(x) wedge above(x,y) wedge x != y
#Add = lift_pos(y)
#Del = lift_pos(x)
def compute_move_down_flags(num_objects):
    person_pos, floor_pos, lift_pos, in_lift_pos, in_floor_pos, above_pos, curr_pos = compute_flag_pos(num_objects)
    move_down_action_flags = [[0] * 4 for i in range(num_objects * num_objects - num_objects)]
    index = 0
    for j in range(0, num_objects):
        for k in range(0, num_objects):
            if (k != j):
                pre = 0
                pre = pre | (1 << (floor_pos + j))
                pre = pre | (1 << (floor_pos + k))
                pre = pre | (1 << (lift_pos + j))
                pre = pre | (1 << (above_pos + j*num_objects + k))
                move_down_action_flags[index][0] = pre
                add = 0
                add = add | (1 << (lift_pos + k))
                move_down_action_flags[index][1] = add
                dele = 0
                dele = dele | (1 << (lift_pos + j))
                move_down_action_flags[index][2] = dele
                move_down_action_flags[index][3] = [j,k]
                index += 1
    return move_down_action_flags

def compute_init_nodes(num_objects, num_floors):
    person_pos, floor_pos, lift_pos, in_lift_pos, in_floor_pos, above_pos, curr_pos = compute_flag_pos(num_objects)
    initnode = 0
    initnode = initnode | (1 << (lift_pos + 0))
    for j in range(0, num_floors):
        initnode = initnode | (1 << (floor_pos + j))
    for j in range(1, num_floors):
        initnode = initnode | (1 << (above_pos + j*num_objects + j-1))
    for j in range(num_floors, num_objects):
        initnode = initnode | (1 << (person_pos + j))
        initnode = initnode | (1 << (in_lift_pos + j))
    return [initnode]

def get_action_names(i):
    names = ["UNBOARD", "BOARD", "MOVEUP", "MOVEDOWN"]
    return names[i]

for num_objects in range (5,9):
    for num_floors in range (3,5):
        unboard_action_flags = compute_unboard_flags(num_objects)
        board_action_flags = compute_board_flags(num_objects)
        move_up_action_flags = compute_move_up_flags(num_objects)
        move_down_action_flags = compute_move_down_flags(num_objects)
        
        node_id = 0
        output_nodes = []
        output_edges = []
        output_connections = []
        num_nodes = 0
        todo_nodes = compute_init_nodes(num_objects, num_floors)
        #build nodes
        while todo_nodes:
            current_node = todo_nodes.pop(0)
            output_nodes.append(current_node)
            num_nodes += 1
            current_edges = []
            connections = 0
            #unboard x,y
            for flags in unboard_action_flags:
                    if current_node & flags[0] == flags[0]:
                        connections += 1
                        target = ((current_node | flags[1]) & ~flags[2])# & all_flags
                        if not ((target in output_nodes) or (target in todo_nodes)):
                            todo_nodes.append(target)
                        current_edges.append([0,target,flags[3]])
            
            #board x,y
            for flags in board_action_flags:
                    if current_node & flags[0] == flags[0]:
                        connections += 1
                        target = ((current_node | flags[1]) & ~flags[2])# & all_flags
                        if not ((target in output_nodes) or (target in todo_nodes)):
                            todo_nodes.append(target)
                        current_edges.append([1,target,flags[3]])
            
            #move x,y,z
            for flags in move_up_action_flags:
                    if current_node & flags[0] == flags[0]:
                        connections += 1
                        target = ((current_node | flags[1]) & ~flags[2])# & all_flags
                        if not ((target in output_nodes) or (target in todo_nodes)):
                            todo_nodes.append(target)
                        current_edges.append([2,target,flags[3]])
            
            #move x,y,z
            for flags in move_down_action_flags:
                    if current_node & flags[0] == flags[0]:
                        connections += 1
                        target = ((current_node | flags[1]) & ~flags[2])# & all_flags
                        if not ((target in output_nodes) or (target in todo_nodes)):
                            todo_nodes.append(target)
                        current_edges.append([3,target,flags[3]])
            
            output_edges.append(current_edges)
            output_connections.append(connections)
        
        #build string
        full_output_string = ""
        output_string = ""
        for i,node in enumerate(output_nodes):
            current_edges = output_edges[i]
            connections = output_connections[i]
            full_node_string = ""
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
                full_node_string += " " + get_action_names(labeled_edge[0]) + "[" + obj_string + "] " + str(index)
                node_string += " " + get_action_names(labeled_edge[0]) + " " + str(index)
            full_output_string += str(connections) + full_node_string + "\n"
            output_string += str(connections) + node_string + "\n"
        full_output_string = "dfa " + str(num_nodes) + " -1\n" + "4 "+get_action_names(0)+" "+get_action_names(1)+" "+get_action_names(2)+" "+get_action_names(3)+"\n" + "1 0\n" + full_output_string
        output_string = "dfa " + str(num_nodes) + " -1\n" + "4 "+get_action_names(0)+" "+get_action_names(1)+" "+get_action_names(2)+" "+get_action_names(3)+"\n" + "1 0\n" + output_string
        filename = "miconic4ops_" + str(num_floors) + "x" + str(num_objects-num_floors) + "_full_label.dfa"
        with open(filename, 'w') as f:
            f.write(full_output_string)
        filename = "miconic4ops_" + str(num_floors) + "x" + str(num_objects-num_floors) + ".dfa"
        with open(filename, 'w') as f:
            f.write(output_string)

        #build string
        full_output_string = ""
        output_string = ""
        for i,node in enumerate(output_nodes):
            full_output_string += "node(" + str(i) + ").\n"
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
                full_output_string += "tlabel(( " + str(i) + ", " + str(index) + "), " +str(labeled_edge[0]+1) + ",(" + obj_string + ")).\n"
                full_output_string += "edge(( " + str(i) + ", " + str(index) + ")).\n"
                output_string += "tlabel(( " + str(i) + ", " + str(index) + "), " +str(labeled_edge[0]+1) + ").\n"
                output_string += "edge(( " + str(i) + ", " + str(index) + ")).\n"
        full_output_string = "labelname("+str(0+1)+",\""+get_action_names(0)+"\").\n" + "labelname("+str(1+1)+",\""+get_action_names(1)+"\").\n" + "labelname("+str(2+1)+",\""+get_action_names(2)+"\").\n" + "labelname("+str(3+1)+",\""+get_action_names(3)+"\").\n" + full_output_string
        output_string = "labelname("+str(0+1)+",\""+get_action_names(0)+"\").\n" + "labelname("+str(1+1)+",\""+get_action_names(1)+"\").\n" + "labelname("+str(2+1)+",\""+get_action_names(2)+"\").\n" + "labelname("+str(3+1)+",\""+get_action_names(3)+"\").\n" + output_string
        filename = "miconic4ops_" + str(num_floors) + "x" + str(num_objects-num_floors) + "_full_label.lp"
        with open(filename, 'w') as f:
            f.write(full_output_string)
        filename = "miconic4ops_" + str(num_floors) + "x" + str(num_objects-num_floors) + ".lp"
        with open(filename, 'w') as f:
            f.write(output_string)

