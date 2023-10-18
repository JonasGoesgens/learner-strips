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

objtuple(( 0, 0, 0),2).% for nullary predicates
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
% Generate scheme

1{prec(A,(P,(OM1,OM2)),X):pred(P),OM1=0..3,OM2=0..3,X=0..1}max_precs   :- action(A).
1{ eff(A,(P,(OM1,OM2)),X):pred(P),OM1=0..3,OM2=0..3,X=0..1}max_effects :- action(A).
:- prec(A,(P,(OM1,OM2)),X), prec(A,(P,(OM1,OM2)),1-X). %No unapplicable actions
:-  eff(A,(P,(OM1,OM2)),X),  eff(A,(P,(OM1,OM2)),1-X). %No contradictory effects
:- prec(A,(P,(OM1,OM2)),X),  eff(A,(P,(OM1,OM2)),  X). %No useless effects

a_atom(1,A,M) :- prec(A,M,X).
a_atom(2,A,M) :- eff(A,M,X).
a_atom(A,M)   :- a_atom(J,A,M), J = 1..2.

a_var(A,V) :- a_atom(A,(_,(V,_))).
a_var(A,V) :- a_atom(A,(_,(_,V))).
:- action(A), a_var(A,V), V > 1, not a_var(A,V-1).
:- action(A), not a_var(A,V) : V = 0..3. % redundant but small

a_arity(A,N)     :- a_var(A,N), not a_var(A,N+1).
a_arity_geq(A,M) :- a_arity(A,N), M = 1..3, N = M..3.

{ unequal(A,(1,2)) }                   :- a_arity_geq(A,2).
{ unequal(A,(1,3)); unequal(A,(2,3)) } :-     a_arity(A,3).

% Inequalities forced by schemas
diff(A,V1,V2) :- eff(A,(P,( V,V1)),X), eff(A,(P,( V,V2)),1-X), V1 < V2.
diff(A,V1,V2) :- eff(A,(P,(V1, V)),X), eff(A,(P,(V2, V)),1-X), V1 < V2.
diff(A,V1,V2) :- eff(A,(P,(V1,V1)),X), eff(A,(P,(V2,V2)),1-X), V1 < V2.
:- diff(A,V1,V2), not unequal(A,(V1,V2)).

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% Predicates

% p_arity(P,N): predicate P has arity N where N in {0..3}
%    p_used(P): predicate P is used in encoding

p_arity(P,2) :- a_atom(_,(P,(V1,V2))), V1 != V2.
p_arity(P,1) :- p_reflexive(P), not p_arity(P,2).
p_arity(P,0) :- a_atom(_,(P,(0,0))).
p_used(P)    :- p_arity(P,_).

p_reflexive(P) :- a_atom(_,(P,(V,V))), V > 0.
:- p_arity(P,X), p_arity(P,Y), Y!=X.
:- p_arity(P,0), p_reflexive(P).
:- p_arity(P,0), p_static(P).    % CHECK: can nullary predicates be static?

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% State Codes
p_min(1,0) :- pred(1).
p_max(P,N) :- not p_used(P), p_min(P,N).
p_max(P,N) :- p_used(P), p_min(P,M), N=M + (num_objects ** A), p_arity(P,A).
p_min(P,N) :- p_max(P-1,N), pred(P), pred(P-1).
state_max(N) :- p_max(max_predicates,M), (2 ** M)=N.

objselect(P,N + ((O1 - 1) * num_objects) + O2 - 1,(O1,O2)) :- p_min(P,N), p_arity(P,2), p_used(P), object(O1), object(O2).
objselect(P,N +   O1 - 1,                         (O1,O1)) :- p_min(P,N), p_arity(P,1), p_used(P), object(O1).
objselect(P,N,                                    (0 ,0 )) :- p_min(P,N), p_arity(P,0), p_used(P).

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% Calc graph properties

numnodes(X) :- {node(S)} = X.

nodereach(N,N)   :- node(N).
nodereach(N1,N2) :- edge((N1,N3)), nodereach(N3,N2), node(N1), node(N2), node(N3).
%Assume strongly conected graph
:- not nodereach(N1,N2), node(N1), node(N2).
%nodereachc(N1,N) :- node(N1), {node(N2):nodereach(N1,N2)} = N.
%nodeusable(N1)   :- node(N1), N {node(N2):nodereachc(N2,C2),C2 <= C1}, nodereachc(N1,C1), numnodes(N + N; N + N - 1).

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% Decompress State

state_val(S,N,S) :- state(S), p_max(max_predicates,N).
state_val(S,N,M) :- N >= 0, state_val(S,N+1,M), M < (2 ** (N+1)).
state_val(S,N,M-(2 ** (N+1))) :- N >= 0, state_val(S,N+1,M), M >= (2 ** (N+1)).

sval((P,OO),S,0) :- M <  (2 ** N), state_val(S,N,M), objselect(P,N,OO).
sval((P,OO),S,1) :- M >= (2 ** N), state_val(S,N,M), objselect(P,N,OO).
sval((P,OO),  V) :- sval((P,OO),S,V), p_static(P), pred(P).
:- sval((P,OO),V),  sval((P,OO),1-V), p_static(P), pred(P).

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% Generate Initial States

possible_state(0..N)  :- state_max(N+1).
{initial_state(S):possible_state(S)}=1.
state(S) :- initial_state(S).
root(S)  :- initial_state(S).
:- state(S), not possible_state(S).

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% Action Applicable?

nappl(A,OO1) :- a_arity_geq(A,2), objtuple(OO1,3), unequal(A,(1,2)), OO1 = (O1,O1,O3).
nappl(A,OO1) :-     a_arity(A,3), objtuple(OO1,3), unequal(A,(1,3)), OO1 = (O1,O2,O1).
nappl(A,OO1) :-     a_arity(A,3), objtuple(OO1,3), unequal(A,(2,3)), OO1 = (O1,O2,O2).

nappl(A,OO1  ) :- sval((P,OO2),  V), map(T,OO1,OO2), prec(A,(P,T),1-V),     p_static(P), pred(P), action(A).
nappl(A,OO1,S) :- nappl(A,OO1), state(S).
% Ground action A(OO1) isn't applicable at S if it contains a false precondition in S
nappl(A,OO1,S) :- sval((P,OO2),S,V), map(T,OO1,OO2), prec(A,(P,T),1-V), not p_static(P), pred(P), action(A).


appl(A,OO1,S) :- action(A), objtuple(OO1,3), state(S), not nappl(A,OO1,S),
                 OO1 = ( 1, 1, 1).
appl(A,OO1,S) :- action(A), objtuple(OO1,3), state(S), not nappl(A,OO1,S),
                 OO1 = (O1, 1, 1), a_arity_geq(A,1), O1 != 1.
appl(A,OO1,S) :- action(A), objtuple(OO1,3), state(S), not nappl(A,OO1,S),
                 OO1 = (O1,O2, 1), a_arity_geq(A,2), O2 != 1.
appl(A,OO1,S) :- action(A), objtuple(OO1,3), state(S), not nappl(A,OO1,S),
                 OO1 = (O1,O2,O3), a_arity_geq(A,3), O3 != 1.

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% Grounded Affects
g_affects_v(A,P,OO1,OO2,X) :- eff(A,(P,T),X), map(T,OO1,OO2).
g_affects(A,P,OO1,OO2) :- g_affects_v(A,P,OO1,OO2,_).

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% Compress next state

next_part(0 ,0,A,OO1,S1) :- appl(A,OO1,S1).
next_part(S2,N,A,OO1,S1) :- appl(A,OO1,S1), next_part(S3 ,N-1,A,OO1,S1), S2=S3+(X * (2 ** (N-1))), objselect(P,N-1,OO2), p_max(max_predicates,M), N>0, N<=M, g_affects_v(A,P,OO1,OO2,X).                     %Effect
next_part(S2,N,A,OO1,S1) :- appl(A,OO1,S1), next_part(S3 ,N-1,A,OO1,S1), S2=S3+(X * (2 ** (N-1))), objselect(P,N-1,OO2), p_max(max_predicates,M), N>0, N<=M, not g_affects(A,P,OO1,OO2), sval((P,OO2),S1,X). %Inertia
state(S2):-next_part(S2,N,A,OO1,S1), p_max(max_predicates,N).
next(A,OO1,S1,S2) :- next_part(S2,N,A,OO1,S1), p_max(max_predicates,N).
construction_check :- {state(S)}=X, numnodes(X).
:- not construction_check.

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% Guess Isomorphism

{isomap(S,N):node(N)}=1 :- state(S), construction_check.                % mapping function
:- node(N), state(S1), state(S2), S1 != S2, isomap(S1,N), isomap(S2,N). % mapping is injective and thus bijective by set size.

:-     next(A,OO1,S1,S2),       not edge((N1,N2)),                          node(N1), node(N2), state(S1), state(S2), isomap(S1,N1), isomap(S2,N2).
:- {next(A,OO1,S1,S2)}=0,           edge((N1,N2)),                          node(N1), node(N2), state(S1), state(S2), isomap(S1,N1), isomap(S2,N2).
:- {next(A,OO1,S1,S2)}=0,     tlabel((N1,N2),A),                          node(N1), node(N2), state(S1), state(S2), isomap(S1,N1), isomap(S2,N2).
:-     next(A,OO1,S1,S2), not tlabel((N1,N2),A), tlabel((N1,N2),B), A!=B, node(N1), node(N2), state(S1), state(S2), isomap(S1,N1), isomap(S2,N2).

val((P,OO2),N,X) :- sval((P,OO2),S1,X), isomap(S,N).
val((P,OO2),  X) :- sval((P,OO2),   X), p_static(P), pred(P).

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% Display

#show action/1.
#show p_arity/2.
#show p_static/1.
#show p_used/1.

#show a_arity/2.
#show unequal/2.
#show labelname/2.
#show prec/3.
#show eff/3.

#show object/1.
#show val(K,S) : val(K,S,1).
#show val(K  ) : val(K,  1).
