num_objects = 2
#predicates
#clear(x)
#ontable(x)
#on(x,y)
#
#actions:
#unstack (x,y) Pre = onblock(x,y) wedge clear(x)
#Add = ontable(x) wedge clear(y)
#Del = onblock(x,y)
#
#stack (x,y) Pre = ontable(x) wedge clear(y) wedge clear(x)
#Add = onblock(x,y)
#Del = ontable(x) wedge clear(y)
curr_pos = 0
clear_pos = curr_pos
curr_pos += num_objects
ontable_pos = curr_pos
curr_pos += num_objects
on_pos = curr_pos
curr_pos += num_objects * num_objects
num_nodes = (1 << curr_pos)
#all_flags = num_nodes - 1
#encoding bittable: clear0,clear1,table0,table1,on00,on01,on10,on11


#build flags
#unstack x,y
unstack_action_flags = [[0] * 3 for i in range(num_objects * num_objects)]
for j in range(0, num_objects):
    for k in range(0, num_objects):
        pre = 0
        pre = pre | (1 << (clear_pos + j))
        pre = pre | (1 << (on_pos + j*num_objects + k))
        unstack_action_flags[j*num_objects+k][0] = pre
        add = 0
        add = add | (1 << (ontable_pos + j))
        add = add | (1 << (clear_pos + k))
        unstack_action_flags[j*num_objects+k][1] = add
        dele = 0
        dele = dele | (1 << (on_pos + j*num_objects + k))
        unstack_action_flags[j*num_objects+k][2] = dele


#stack x,y
stack_action_flags = [[0] * 3 for i in range(num_objects * num_objects)]
for j in range(0, num_objects):
    for k in range(0, num_objects):
        pre = 0
        pre = pre | (1 << (ontable_pos + j))
        pre = pre | (1 << (clear_pos + j))
        pre = pre | (1 << (clear_pos + k))
        stack_action_flags[j*num_objects+k][0] = pre
        add = 0
        add = add | (1 << (on_pos + j*num_objects + k))
        stack_action_flags[j*num_objects+k][1] = add
        dele = 0
        dele = dele | (1 << (ontable_pos + j))
        dele = dele | (1 << (clear_pos + k))
        stack_action_flags[j*num_objects+k][2] = dele

output_string = ""
#build nodes
for i in range(0, num_nodes):
    connections = 0
    node_string = ""
    #unstack x,y
    for j in range(0, num_objects):
        for k in range(0, num_objects):
            if i & unstack_action_flags[j*num_objects+k][0] == unstack_action_flags[j*num_objects+k][0]:
                connections += 1
                target = ((i | unstack_action_flags[j*num_objects+k][1]) & ~unstack_action_flags[j*num_objects+k][2])# & all_flags
                node_string += " unstack " + str(target)
    #stack x,y
    for j in range(0, num_objects):
        for k in range(0, num_objects):
            if i & stack_action_flags[j*num_objects+k][0] == stack_action_flags[j*num_objects+k][0]:
                connections += 1
                target = ((i | stack_action_flags[j*num_objects+k][1]) & ~stack_action_flags[j*num_objects+k][2])# & all_flags
                node_string += " stack " + str(target)
    output_string += str(connections) + node_string + "\n"
output_string = "dfa " + str(num_nodes) + " -1\n" + "2 unstack stack\n" + "1 0\n" + output_string
with open('blocks2ops2_noconstraints.dfa', 'w') as f:
    f.write(output_string)
