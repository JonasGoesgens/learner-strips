num_objects = 2
#predicates
#clear(x)
#on(x,y)
#p1(x1)
#p2(x1, x2)

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

#Static: neq(x1, x2)
#Pre = p1(x2), p2(x2, x2)
#Add = p2(x1, x1), p2(x2, x1)
#Del = p1(x2),
def compute_unstack_flags(num_objects):
    clear_pos, on_pos, curr_pos = compute_flag_pos(num_objects)
    unstack_action_flags = [[0] * 3 for i in range(num_objects * num_objects - num_objects)]
    index = 0
    for j in range(0, num_objects):
        for k in range(0, num_objects):
            if (k != j):
                pre = 0
                pre = pre | (1 << (clear_pos + k))
                pre = pre | (1 << (on_pos + k*num_objects + k))
                unstack_action_flags[index][0] = pre
                add = 0
                add = add | (1 << (on_pos + j*num_objects + j))
                add = add | (1 << (on_pos + k*num_objects + j))
                unstack_action_flags[index][1] = add
                dele = 0
                dele = dele | (1 << (clear_pos + k))
                unstack_action_flags[index][2] = dele
                index += 1
    return unstack_action_flags

#stack x,y
#Pre = onblock(x,x) wedge clear(y) wedge clear(x) wedge x != y
#Add = onblock(x,y)
#Del = onblock(x,x) wedge clear(y)

#Static: neq(x1, x2)
#Pre = p2(x1, x1), p2(x1, x2), p2(x2, x2)
#Add = p1(x1),
#Del = p2(x2, x2)
def compute_stack_flags(num_objects):
    clear_pos, on_pos, curr_pos = compute_flag_pos(num_objects)
    stack_action_flags = [[0] * 3 for i in range(num_objects * num_objects - num_objects)]
    index = 0
    for j in range(0, num_objects):
        for k in range(0, num_objects):
            if (k != j):
                pre = 0
                pre = pre | (1 << (on_pos + j*num_objects + j))
                pre = pre | (1 << (on_pos + j*num_objects + k))
                pre = pre | (1 << (on_pos + k*num_objects + k))
                stack_action_flags[index][0] = pre
                add = 0
                add = add | (1 << (clear_pos + j))
                stack_action_flags[index][1] = add
                dele = 0
                dele = dele | (1 << (on_pos + k*num_objects + k))
                stack_action_flags[index][2] = dele
                index += 1
    return stack_action_flags

unstack_action_flags = compute_unstack_flags(num_objects)
stack_action_flags = compute_stack_flags(num_objects)

num_nodes = compute_num_nodes(num_objects)
output_string = ""
dot_output_string = ""
#build nodes
for i in range(0, num_nodes):
    connections = 0
    node_string = ""
    dot_node_string = "N" + str(i)
    #unstack x,y
    b_edge = False
    for flags in unstack_action_flags:
        if (i & flags[0]) == flags[0]:
            connections += 1
            target = ((i | flags[1]) & ~flags[2])# & all_flags
            node_string += " unstack " + str(target)
            if not b_edge:
                dot_node_string += " -> { "
                b_edge = True
            dot_node_string += "N" + str(target) + " " 
    if b_edge:
        dot_node_string += "} [color=red]\nN" + str(i)
        b_edge = False
    #stack x,y
    for flags in stack_action_flags:
        if (i & flags[0]) == flags[0]:
            connections += 1
            target = ((i | flags[1]) & ~flags[2])# & all_flags
            node_string += " stack " + str(target)
            if not b_edge:
                dot_node_string += " -> { "
                b_edge = True
            dot_node_string += "N" + str(target) + " " 
    if b_edge:
        dot_node_string += "} [color=blue]"
        b_edge = False
    output_string += str(connections) + node_string + "\n"
    dot_output_string += dot_node_string + "\n"
dot_output_string = "digraph { \n" + dot_output_string + "}"
output_string = "dfa " + str(num_nodes) + " -1\n" + "2 unstack stack\n" + "1 0\n" + output_string
with open('blocksmin2ops2_noconstraints_conflict.dfa', 'w') as f:
    f.write(output_string)

with open('blocksmin2ops2_noconstraints_conflict.dot', 'w') as f:
    f.write(dot_output_string)
