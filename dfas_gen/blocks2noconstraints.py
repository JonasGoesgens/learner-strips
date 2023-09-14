num_objects = 2
#predicates
#handfree()
#grabbed(x)
#clear(x)
#ontable(x)
#on(x,y)
#
#actions:
#get (x) Pre = ontable(x) wedge clear(x) wedge handfree()
#Add = grabbed(x)
#Del = ontable(x) wedge clear(x) wedge handfree()
#
#put (x) Pre = grabbed(x)
#Add = ontable(x) wedge clear(x) wedge handfree()
#Del = grabbed(x)
#
#unstack (x,y) Pre = onblock(x,y) wedge clear(x) wedge handfree()
#Add = grabbed(x) wedge clear(y)
#Del = onblock(x,y) wedge clear(x) wedge handfree()
#
#stack (x,y) Pre = grabbed(x) wedge clear(y)
#Add = onblock(x,y) wedge clear(x) wedge handfree()
#Del = grabbed(x) wedge clear(y)
curr_pos = 0
handfree_pos = curr_pos
curr_pos += 1
grabbed_pos = curr_pos
curr_pos += num_objects
clear_pos = curr_pos
curr_pos += num_objects
ontable_pos = curr_pos
curr_pos += num_objects
on_pos = curr_pos
curr_pos += num_objects * num_objects
num_nodes = (1 << curr_pos)
#all_flags = num_nodes - 1
#encoding bittable handfree,grabbed0,grabbed1,clear0,clear1,table0,table1,on00,on01,on10,on11


#build flags
get_action_flags = [[0] * 3 for i in range(num_objects)]
for j in range(0, num_objects):
    int pre = 0
    pre = pre | (1 << handfree_pos)
    pre = pre | (1 << (clear_pos + j))
    pre = pre | (1 << (table_pos + j))
    get_action_flags[j][0] = pre
    int add = 0
    add = add | (1 << (grabbed_pos + j))
    get_action_flags[j][1] = add
    int dele = 0
    dele = dele | (1 << handfree_pos)
    dele = dele | (1 << (clear_pos + j))
    dele = dele | (1 << (table_pos + j))
    get_action_flags[j][2] = dele

#put x
put_action_flags = [[0] * 3 for i in range(num_objects)]
for j in range(0, num_objects):
    int pre = 0
    pre = pre | (1 << (grabbed_pos + j))
    put_action_flags[j][0] = pre
    int add = 0
    add = add | (1 << handfree_pos)
    add = add | (1 << (clear_pos + j))
    add = add | (1 << (table_pos + j))
    put_action_flags[j][1] = add
    int dele = 0
    dele = dele | (1 << (grabbed_pos + j))
    put_action_flags[j][2] = dele


#unstack x,y
unstack_action_flags = [[0] * 3 for i in range(num_objects * num_objects)]
for j in range(0, num_objects):
    for k in range(0, num_objects):
        int pre = 0
        pre = pre | (1 << handfree_pos)
        pre = pre | (1 << (clear_pos + j))
        pre = pre | (1 << (on_pos + j*num_objects + k))
        unstack_action_flags[j*num_objects+k][0] = pre
        int add = 0
        add = add | (1 << (grabbed_pos + j))
        add = add | (1 << (clear_pos + k))
        unstack_action_flags[j*num_objects+k][1] = add
        int dele = 0
        dele = dele | (1 << handfree_pos)
        dele = dele | (1 << (clear_pos + j))
        dele = dele | (1 << (on_pos + j*num_objects + k))
        unstack_action_flags[j*num_objects+k][2] = dele


#stack x,y
stack_action_flags = [[0] * 3 for i in range(num_objects * num_objects)]
for j in range(0, num_objects):
    for k in range(0, num_objects):
        int pre = 0
        pre = pre | (1 << (grabbed_pos + j))
        pre = pre | (1 << (clear_pos + k))
        stack_action_flags[j*num_objects+k][0] = pre
        int add = 0
        add = add | (1 << handfree_pos)
        add = add | (1 << (clear_pos + j))
        add = add | (1 << (on_pos + j*num_objects + k))
        stack_action_flags[j*num_objects+k][1] = add
        int dele = 0
        dele = dele | (1 << (grabbed_pos + j))
        dele = dele | (1 << (clear_pos + k))
        stack_action_flags[j*num_objects+k][2] = dele

output_string = ""
#build nodes
for i in range(0, num_nodes):
    connections = 0
    node_string = ""
    #get x
    for j in range(0, num_objects):
        if i & get_action_flags[j][0] == get_action_flags[j][0]:
            connections += 1
            target = ((i | get_action_flags[j][1]) & ~get_action_flags[j][2])# & all_flags
            node_string += " get " + str(target)
    #put x
    for j in range(0, num_objects):
        if i & put_action_flags[j][0] == put_action_flags[j][0]:
            connections += 1
            target = ((i | put_action_flags[j][1]) & ~put_action_flags[j][2])# & all_flags
            node_string += " put " + str(target)
    #unstack x,y
    for j in range(0, num_objects):
        for k in range(0, num_objects):
            if i & unstack_action_flags[j*num_objects+k][0] == unstack_action_flags[j*num_objects+k][0]:
                connections += 1
                target = ((i | unstack_action_flags[j*num_objects+k][1]) & ~unstack_action_flags[j*num_objects+k][2])# & all_flags
                node_string += " put " + str(target)
    #stack x,y
    for j in range(0, num_objects):
        for k in range(0, num_objects):
            if i & stack_action_flags[j*num_objects+k][0] == stack_action_flags[j*num_objects+k][0]:
                connections += 1
                target = ((i | stack_action_flags[j*num_objects+k][1]) & ~stack_action_flags[j*num_objects+k][2])# & all_flags
                node_string += " put " + str(target)
    output_string += str(connections) + node_string + "\n"
output_string = "dfa " + str(num_nodes) + " -1\n" + "4 get put unstack stack\n" + "1 0\n" + output_string
with open('blocks2noconstraints.dfa', 'w') as f:
    f.write(output_string)
