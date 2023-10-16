%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% Constants

% Allocate max_predicates predicates of which the last max_static are
% static predicates. Some predicates may be left unused; these will be
% the last ones in each block of fluent or static predicates.

% max_precs and max_effects bound the number of preconditions and effects
% for each action.

#const max_predicates=5. % total number of predicates
#const max_static=2.     % these last number of predicates are static
#const max_precs=6.      % for each action
#const max_effects=6.    % for each action
#const opt_unequal=1.    % inequality constraints for action arguments
#const opt_synthesis=1.  % enable synthesis of model

% Constants needed and set at call time:
%#const num_objects >= 1


%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% Predicates and static predicates (p_static), objects and actions

pred(1..max_predicates).
p_static(max_predicates-max_static+1..max_predicates).
:- p_static(P), P = 1..max_predicates-max_static.
object(1..num_objects).
action(1..N) :- num_actions(N).
#defined num_actions/1.

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% Action Predicate mapping

objtuple(( 0, 0, 0),3).% for nullary predicates
objtuple((O1,O2,O3),3) :- object(O1), object(O2), object(O3).

map((0,0),(O1,O2,O3),( 0, 0)) :- objtuple((O1,O2,O3),3). % for nullary predicates
map((1,1),(O1,O2,O3),(O1,O1)) :- objtuple((O1,O2,O3),3).
map((1,2),(O1,O2,O3),(O1,O2)) :- objtuple((O1,O2,O3),3).
map((1,3),(O1,O2,O3),(O1,O3)) :- objtuple((O1,O2,O3),3).
map((2,1),(O1,O2,O3),(O2,O1)) :- objtuple((O1,O2,O3),3).
map((2,2),(O1,O2,O3),(O2,O2)) :- objtuple((O1,O2,O3),3).
map((2,3),(O1,O2,O3),(O2,O3)) :- objtuple((O1,O2,O3),3).
map((3,1),(O1,O2,O3),(O3,O1)) :- objtuple((O1,O2,O3),3).
map((3,2),(O1,O2,O3),(O3,O2)) :- objtuple((O1,O2,O3),3).
map((3,3),(O1,O2,O3),(O3,O3)) :- objtuple((O1,O2,O3),3).

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%Generate scheme

1{prec(A,(P,(OM1,OM2)),X):pred(P),OM1=0..3,OM2=0..3,X=0..1}max_precs   :- action(A).
1{ eff(A,(P,(OM1,OM2)),X):pred(P),OM1=0..3,OM2=0..3,X=0..1}max_effects :- action(A).
:- prec(A,(P,(OM1,OM2)),X, prec(A,(P,(OM1,OM2)),1-X. %No unapplicable actions
:-  eff(A,(P,(OM1,OM2)),X,  eff(A,(P,(OM1,OM2)),1-X. %No contradictory effects
:- prec(A,(P,(OM1,OM2)),X,  eff(A,(P,(OM1,OM2)),  X. %No useless effects

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%Calc graph properties

numnodes(X) :- {node(S)} = X.

nodereach(S,S)   :- node(S).
nodereach(S1,S2) :- edge(S1,S3), nodereach(S3,S2), node(S1), node(S2), node(S3).
nodereachc(S1,N) :- node(S1), {node(S2):nodereach(S1,S2)} = N.
nodeusable(S1)   :- node(S1), N {node(S2):nodereachc(S2,C2),C2 <= C1}, nodereachc(S1,C1), numnodes(N+N;N+N-1).

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%Generate States

state(1..N):- numnodes(N).
{val((P,(0,0)),S,V):V=0..1} = 1 :- state(S),pred(P),p_arity(P,0),S=1.
{val((P,(O1,O1)),S,V):V=0..1} = 1 :- state(S),pred(P),p_arity(P,1),object(O1),S=1.
{val((P,(O1,O2)),S,V):V=0..1} = 1 :- state(S),pred(P),p_arity(P,2),object(O1),object(O2),S=1.


nappl(A,OO1  ) :- val((P,OO2),  V), map(T,OO1,OO2), prec(A,(P,T),1-V),     p_static(P), pred(P), action(A).
nappl(A,OO1,S) :- nappl(A,OO1), state(S).
% Ground action A(OO1) isn't applicable at S if it contains a false precondition in S
nappl(A,OO1,S) :- val((P,OO2),S,V), map(T,OO1,OO2), prec(A,(P,T),1-V), not p_static(P), pred(P), action(A).
