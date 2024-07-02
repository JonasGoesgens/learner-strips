labelname(1,"MOVE").
labelname(2,"PICK").
labelname(3,"DROP").
node(0).
node(1).
node(2).
node(3).
node(4).
node(5).
node(6).
node(7).
tlabel((0, 1), 2,(1,2,3)).
tlabel((0, 2), 2,(1,2,4)).
tlabel((0, 3), 1,(2,5,0)).
tlabel((1, 0), 3,(1,2,3)).
tlabel((1, 4), 1,(2,5,0)).
tlabel((2, 0), 3,(1,2,4)).
tlabel((2, 5), 1,(2,5,0)).
tlabel((3, 0), 1,(5,2,0)).
tlabel((4, 6), 3,(1,5,3)).
tlabel((4, 1), 1,(5,2,0)).
tlabel((5, 6), 3,(1,5,4)).
tlabel((5, 2), 1,(5,2,0)).
tlabel((6, 4), 2,(1,5,3)).
tlabel((6, 5), 2,(1,5,4)).
tlabel((6, 7), 1,(5,2,0)).
tlabel((7, 6), 1,(2,5,0)).
edge((0,1)).
edge((0,2)).
edge((0,3)).
edge((1,0)).
edge((1,4)).
edge((2,0)).
edge((2,5)).
edge((3,0)).
edge((4,6)).
edge((4,1)).
edge((5,6)).
edge((5,2)).
edge((6,4)).
edge((6,5)).
edge((6,7)).
edge((7,6)).
