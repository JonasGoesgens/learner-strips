% we use the same format of input as before but we use the objects that the action is used with where the order is crutial 
% constants that may be needed 
#const max_predicates   =  5. 
#const max_influence    =  8. % how many predicates of the same kind can be changed by one action (BSP: how many on(x,y) predicates in blocks, move needs 2) 
#const max_static       =  2.
#const max_precondition = 10. 

% how to run the files 
% srun -p rleap_gpu_24gb --pty -c 64 apptainer shell --bind ./learner-strips/:/learner-strips/ test.sif
% srun -p rleap_gpu_24gb --pty -c 64 starte auf freiem rleap cluster node interactiv mit 64 cpu cores
% apptainer shell --bind ./learner-strips/:/learner-strips/ test.sif apptaint mit shell fuer eigene Komandos mounted das learner-strips Verzeichnis mit conainer file test.sif
% 
% im aptainer:  cd /learner-strips/ also in den ordner rein 
% clingo -t 64 blocksmin3ops3.lp dual.lp 
% python3 debug_clingo.py -n 2 blocksmin3ops2.lp dual.lp 

% get objects from labels 
object(O) :- tlabel(_,_,(O,_,_)), O > -1.
object(O) :- tlabel(_,_,(_,O,_)), O > -1.
object(O) :- tlabel(_,_,(_,_,O)), O > -1.


% we have the actions given by the graph 
% the actions have some artity 
% !!! arity has to be fixed 
action(A) :- tlabel(_,A,_). 

% what happens if O1 = O2 = O3 of arity 3 that is executed with arity 1  ... 
a_arity(A,0) :- tlabel(_,A,(-1,-1,-1)).
a_arity(A,1) :- tlabel(_,A,(O1,-1,-1)), object(O1).
a_arity(A,2) :- tlabel(_,A,(O1,O2,-1)), object(O1), object(O2).
a_arity(A,3) :- tlabel(_,A,(O1,O2,O3)), object(O1), object(O2), object(O3). 

:- a_arity(A,I), a_arity(A,J), I != J. % i dont know if can happen... 

% get equal for preconditions/ applicable actions 
equal(A,1,2) :- tlabel(_,A,(O1,O1,_)), object(O1).
equal(A,1,3) :- tlabel(_,A,(O1,_,O1)), object(O1).
equal(A,2,3) :- tlabel(_,A,(_,O1,O1)), object(O1). 

% unequal of two actions 
unequal(A,N1,N2) :- not equal(A,N1,N2), action(A), N1=1..3, N2=1..3, N1 < N2. 

% Predicates 
% we need to guess the predicates (and use the optimization given so the smallest solution is used)
predicate(1..max_predicates). 
p_static(max_predicates-max_static+1..max_predicates).
p_not_static(1..max_predicates-max_static). 

:- p_static(P), p_not_static(P).


% p_arity(P,N): predicate P has arity N where N in {0..3}
%    p_used(P): predicate P is used in encoding
{usedpredicates(N) : N = 1..max_predicates}=1.
p_used(P):- usedpredicates(N), P=1..N.
{p_arity(P,0..2)} = 1 :- predicate(P), p_used(P).  
%p_used(P) :- predicate(P), p_arity(P,_).

% tupel of objects 
objtuple((-1,-1), 2). % for nullary predicates
objtuple((O1,O2), 2) :- object(O1), object(O2). % for features with arity 1 or two 

% tupel of actions since everything on the left has to be on the right (???) 
%action_tupel((O1,O2,O3)) :- tlabel(_,_,(O1,O2,O3)). % 
action_tupel((O1,O2,O3)) :- object(O1) , object(O2), object(O3).
action_tupel((O1,O2,O3)) :- object(O1) , object(O2),    O3 = -1.
action_tupel((O1,O2,O3)) :- object(O1) ,    O2 = -1,    O3 = -1.
action_tupel((O1,O2,O3)) :-    O1 = -1 ,    O2 = -1,    O3 = -1.

action_tupel_size((-1,-1,-1),0).
action_tupel_size((O1,-1,-1),1) :- object(O1).
action_tupel_size((O1,O2,-1),2) :- object(O1) , object(O2).
action_tupel_size((O1,O2,O3),3) :- object(O1) , object(O2), object(O3).

% mapping maps object_tupel with given pattern to a new tupel  
map((-1,-1),(O1,O2,O3), (-1,-1)) :- action_tupel((O1,O2,O3)). % dont know if this is right 
map(( 1, 1),(O1,O2,O3), (O1,O1)) :- action_tupel((O1,O2,O3)), object(O1).
map(( 1, 2),(O1,O2,O3), (O1,O2)) :- action_tupel((O1,O2,O3)), object(O1), object(O2).
map(( 1, 3),(O1,O2,O3), (O1,O3)) :- action_tupel((O1,O2,O3)), object(O1),             object(O3).
map(( 2, 1),(O1,O2,O3), (O2,O1)) :- action_tupel((O1,O2,O3)), object(O1), object(O2).
map(( 2, 2),(O1,O2,O3), (O2,O2)) :- action_tupel((O1,O2,O3))            , object(O2).
map(( 2, 3),(O1,O2,O3), (O2,O3)) :- action_tupel((O1,O2,O3))            , object(O2), object(O3).
map(( 3, 1),(O1,O2,O3), (O3,O1)) :- action_tupel((O1,O2,O3)), object(O1)            , object(O3).
map(( 3, 2),(O1,O2,O3), (O3,O2)) :- action_tupel((O1,O2,O3))            , object(O2), object(O3).
map(( 3, 3),(O1,O2,O3), (O3,O3)) :- action_tupel((O1,O2,O3))                        , object(O3).

% change pattern how the objects of an action change the predicate 
pattern(0, J,  (-1,-1))    :- J=0..3.
pattern(1, J,  (N1,N1))    :- J=1..3,N1 = 1..J.
pattern(2, J,  (N1,N2))    :- J=1..3,N1 = 1..J, N2 = 1..J.

% we need to guess for each predicate which actions add it and which actions delete it 
% this is similar as choosing which action changes which predicate. 
{changes(A,P,0..1)} = 1 :- action(A), predicate(P), p_used(P). % each action either changes or does not change each predicate

% if a actions changes a predicate it either makes it true or false and it does it by a fixed pattern 
% e.g. a(x,y,z) makes p1(z,y) and p2(y) and p3(x,z) true or false ... 
% it has to change at least 1 predicate and at most max_influence
% there should be something that delets patterns that add and delete the same feature 
0 {change_pattern(A,P,Pattern,0..1): pattern(I, J, Pattern)} max_influence :- changes(A,P,1), p_arity(P,I), a_arity(A,J), I <= J.
:-   {change_pattern(A,P,Pattern,0..1)} = 0, changes(A,P,1). 
:- 1 {change_pattern(A,P,Pattern,0..1)}    , changes(A,P,0). 

% there can not be any feature be added and deleted by the same action 
:- change_pattern(A,P,Pattern,0), change_pattern(A,P,Pattern,1).

% there cannot be a change pattern that changes p(O1,O2) with O1 != O2 when p has arity 1 
:- change_pattern(_,P,(O1,O2),_), p_arity(P,1), O1 != O2. 

% there cannot be a change pattern on object for a feature of arity 0 
:- change_pattern(_,P,(O1,O2),_), p_arity(P,0), O1 != -1, O2 != -1. 


% a value of an predicate has to be 0/1 at least once each 
1 {val(S,(P,(O1,O2)),1):node(S)}:-object(O1), object(O2), predicate(P), p_used(P), p_arity(P,2).
1 {val(S,(P,(O1,O2)),0):node(S)}:-object(O1), object(O2), predicate(P), p_used(P), p_arity(P,2).
1 {val(S,(P,(O1,O1)),1):node(S)}:-object(O1),             predicate(P), p_used(P), p_arity(P,1).
1 {val(S,(P,(O1,O1)),0):node(S)}:-object(O1),             predicate(P), p_used(P), p_arity(P,1).
1 {val(S,(P,(-1,-1)),1):node(S)}:-                        predicate(P), p_used(P), p_arity(P,0).
1 {val(S,(P,(-1,-1)),0):node(S)}:-                        predicate(P), p_used(P), p_arity(P,0).

% there can not be an action that has no effect 
:- action(A), {change_pattern(A,_,_,_)} = 0. 

% each predicate needs to be added and deleted at some point (static is missing)
:- predicate(P), p_used(P), p_not_static(P), p_used(P), {change_pattern(_,P,_,0)} = 0.
:- predicate(P), p_used(P), p_not_static(P), p_used(P), {change_pattern(_,P,_,1)} = 0.


% values of the features at a node S1 is defined if there is an edge with the given labels (change (forward) + neutral (forward + backward))
val(S1,(P,OList),V) :- node(S1), node(S2), predicate(P), p_used(P), tlabel((S2,S1),A,Obj), map(Pattern, Obj,OList),  change_pattern(A,P,Pattern,V).
val(S1,(P,OList),V) :- node(S1), node(S2), predicate(P), p_used(P), tlabel((S2,S1),A,Obj), map(Pattern, Obj,OList), {change_pattern(A,P,Pattern,_)} = 0, val(S2,(P,OList),V). 
val(S1,(P,OList),V) :- node(S1), node(S2), predicate(P), p_used(P), tlabel((S1,S2),A,Obj), map(Pattern, Obj,OList), {change_pattern(A,P,Pattern,_)} = 0, val(S2,(P,OList),V). 
val(S1,(P,OList),V) :- node(S1), node(S2), predicate(P), p_used(P), tlabel((S1,S2),A,Obj), {map(Pattern, Obj,OList)} = 0, val(S2,(P,OList),V). 

% at every state the value of a predicate for fixed objects can not be true and false at the same time 
:- val(S1,(P,O),V), val(S1,(P,O),W), W != V. 

% the value of each feature of arity 1 is false for all O1 != O2 
:- val(S,(P,(O1,O2)),1), not p_arity(P,2), O1 != O2.

% the value of a feature of arity 0 is false for all objects 
p_arity_1_or_2(P) :- p_arity(P,N), N = 1..2.

:- val(S,(P,(O,_)),1), p_arity(P,0), O != -1.
:- val(S,(P,(_,O)),1), p_arity(P,0), O != -1.

% set unset values to -1 #currently not used# 
%val(S,(P,(O1,O2)),-1) :- {val(S,(P,(O1,O2)),0);val(S,(P,(O1,O2)),1)} = 0, node(S) , predicate(P), object(O1), object(O2).

% two different states need to have 2 different values
:- node(S1), node(S2), S1 < S2, val(S1,(P,T),V) : val(S2,(P,T),V).

% each action needs to have some precondition but at most max_precondition many 
1 {precondition(A,P,Pattern,V): predicate(P), p_used(P), pattern(_,_,Pattern), V=0..1} max_precondition :- action(A).

% there cant be a negative and positive precontion on the same elements 
:- precondition(A,P,Pattern,0), precondition(A,P,Pattern,1). 

% each effect must be part of the precondition 
:- node(S1), predicate(P), p_used(P), action(A), pattern(_,_,Pattern), change_pattern(A,P,Pattern,0), not precondition(A,P,Pattern,1). 
:- node(S1), predicate(P), p_used(P), action(A), pattern(_,_,Pattern), change_pattern(A,P,Pattern,1), not precondition(A,P,Pattern,0). 

% each state that fullfills an precondition needs that label in the graph 
n_apply(A,S1,AOlist) :- node(S1), action(A), predicate(P), p_used(P), precondition(A,P,Pattern,V), not val(S1,(P,POlist),V), map(Pattern, AOlist, POlist).
n_apply(A,S1,AOlist) :- node(S1), action(A), a_arity(A,X), action_tupel_size(AOlist,Y), X != Y. 

% unequal preconditions 
n_apply(A,S1,(O1,O2,O3)) :- node(S1), action(A), object(O1), object(O2), unequal(A,1,2), action_tupel((O1,O2,O3)), O1 = O2.
n_apply(A,S1,(O1,O2,O3)) :- node(S1), action(A), object(O1), object(O3), unequal(A,1,3), action_tupel((O1,O2,O3)), O1 = O3.
n_apply(A,S1,(O1,O2,O3)) :- node(S1), action(A), object(O2), object(O3), unequal(A,2,3), action_tupel((O1,O2,O3)), O2 = O3.

% each action that is in the graph has to have a corresponding edge adn each action not applicable can not have a edge in the graph 
:- node(S1), action(A), action_tupel(AOlist), n_apply(A,S1,AOlist), tlabel((S1,_),A,AOlist).
:- node(S1), action(A), action_tupel(AOlist), not n_apply(A,S1,AOlist), not tlabel((S1,S2),A,AOlist):node(S2).


% TODO List.  
% -what if val of S2 is not set for all differing predicates (im moment geraten) 
% -what is happening with static predicates (TODO)
% -we do not need them to guess the effects of some action, e.g. they cannot be added or deleted therefore there is the 
% -question that we do actually need them for the first tests. 
% -minimization (works for now/ work in progress)
% -weiter aufraeumen (nicht genutzten code entfernen + bessere kommentare)
% -git pushen wenn progress 


% define things that should be printed after solving 
#show a_arity/2.
#show precondition/4.
#show change_pattern/4.
#show val(S1,(P,OList),V): val(S1,(P,OList),V), S1 = 0.
#show pattern/3.
#show p_arity/2. 
#show usedpredicates/1.


%changes: 
% there cant be action tupels that have the same element at different positions (besides -1 )
% we have a function for the length of an action tupel to better say when an action is applicable 
% minimisation precondtions 