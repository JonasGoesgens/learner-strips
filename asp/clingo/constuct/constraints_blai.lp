% Break symmetries for predicates
:- p_arity(P, X), p_arity(P+1, Y), X > Y, P=1..max_predicates-max_static-1.
:- not p_used(P), p_used(P+1), P=1..max_predicates-max_static-1.
:- p_arity(P, X), p_arity(P+1, Y), X > Y, P=max_predicates-max_static+1..max_predicates-1.
:- not p_used(P), p_used(P+1), P=max_predicates-max_static+1..max_predicates-1.

% Non-static predicates must differ at some state
:- pred(P), not p_static(P), p_arity(P, 0), root(R), {sval((P, ( 0,  0)), S, X) : state(S),                         sval((P, ( 0,  0)), R, 1-X), S != R} = 0.
:- pred(P), not p_static(P), p_arity(P, 1), root(R), {sval((P, ( O,  O)), S, X) : state(S), object( O),             sval((P, ( O,  O)), R, 1-X), S != R} = 0.
:- pred(P), not p_static(P), p_arity(P, 2), root(R), {sval((P, (O1, O2)), S, X) : state(S), object(O1), object(O2), sval((P, (O1, O2)), R, 1-X), S != R} = 0.

