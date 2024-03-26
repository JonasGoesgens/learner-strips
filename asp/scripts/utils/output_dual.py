from typing import List
import clingo
import sys
import re
from utils.names import *

# create from output_vars 
# 413: get_string is missing 
# python3 incremental_solver.py --threads=64 --no_invariants --version kr21 benchmarks/match2ops_4_full_label_1r.txt --results results/ 0




CHANGE_PATTERN = ('changes', 4)
PREC_4 = ('prec', 4)
P_ARITY_2 = ('p_arity', 2)
P_USED = ('p_used', 1)
USED_PREDICATES = ('usedpredicates', 1)
USED_STATIC_PREDICATES = ('usedstaticpredicates', 1)

def map_to_number(ints):
    return tuple(map(lambda x: clingo.Number(x), ints))

def change_pattern(action,predicate,pattern,value): 
    p1, p2 = pattern
    return clingo.Function('precondition', [clingo.Number(action), clingo.Number(predicate), clingo.Function('', [clingo.Number(p1),clingo.Number(p2)]), clingo.Number(value)])

def precondition(action,predicate,pattern,value): 
    p1, p2 = pattern
    return clingo.Function('precondition', [clingo.Number(action), clingo.Number(predicate), clingo.Function('', [clingo.Number(p1),clingo.Number(p2)]), clingo.Number(value)])

def n_use_predicates(n): 
    return clingo.Function('usedpredicates', map_to_number([n]))

def n_used_static_predicates(n): 
    return clingo.Function('usedstaticpredicates', map_to_number([n]))

def p_arity(p,arity): 
    return clingo.Function('p_arity', map_to_number([p,arity]))

def p_used(p):
    return clingo.Function('p_used', map_to_number([p]))

class STRIPSSchema:
    def __init__(self, root = 0):
        self._change_pattern = []
        self._precs = []
        self._p_arity = {}
        self._p_used = set()
        self._actions = set() 
        self._predicates = {}
        self._n_used_predicates = set()
        self._n_used_static_predicates = set()
        # self.__root = root 

    def get_root(self):
        return self.__root
    
    def set_root(self, root):
        self.__root = root

    def add_action(self, a): 
        if a not in self._actions: 
            self._actions.add(a)

    def add_predicate(self, predicate):
        if predicate not in self._predicates:
            self._predicates[predicate] = 2 # default

    def set_predicate_arity(self, predicate, arity):
        self.add_predicate(predicate)
        self._predicates[predicate] = arity

    def set_change_pattern(self, action, predicate, pattern, value):
        self.add_action(action) 
        arr = [action, predicate, pattern, value]
        if arr not in self._change_pattern: 
            self._change_pattern.append(arr)

    def set_n_used_predicates(self,p): 
        self._n_used_predicates.add(p)

    def set_n_used_static_predicates(self,p): 
        self._n_used_static_predicates.add(p)
    
    def add_used_predicate(self, p):   
        self._p_used.add(p)
    
    def set_prec(self, action, predicate, pattern, value): 
        self.add_action(action)
        arr = [action, predicate, pattern, value]
        if arr not in self._change_pattern: 
            self._precs.append(arr)
    
    # get with index
    def get_change_pattern(self,i): 
        if i >= 0 and i <= len(self._change_pattern): 
            a, p, pattern, value = self._change_pattern[i]
            return {'action':a, 'predicate': p, 'pattern':pattern,'value':value}
        

    @classmethod
    def create_from_clingo(cls, symbols : List[clingo.Symbol]):
        others = []
        schema = cls()
        # vals = []
        for symbol in symbols:
            if symbol.type != clingo.SymbolType.Function:
                others.append(symbol)
            elif symbol.match(*P_ARITY_2):
                p, arity = symbol.arguments
                schema.set_predicate_arity(p.number, arity.number)
            elif symbol.match(*PREC_4): 
                action, p, pattern, v = symbol.arguments
                p1,p2 = pattern.arguments
                schema.set_prec(action.number, p.number, (p1.number,p2.number) ,v.number) 
            elif symbol.match(*P_USED): 
                p, = symbol.arguments
                schema.add_used_predicate(p.number)
            elif symbol.match(*CHANGE_PATTERN): 
                action, p, pattern, v = symbol.arguments
                p1,p2 = pattern.arguments
                schema.set_change_pattern(action.number, p.number, (p1.number,p2.number) ,v.number) 
            elif symbol.match(*USED_PREDICATES): 
                n, = symbol.arguments
                schema.set_n_used_predicates(n.number) 
            elif symbol.match(*USED_STATIC_PREDICATES): 
                n, = symbol.arguments
                schema.set_n_used_static_predicates(n.number) 



        # root = schema.get_root()
        # for inst, (p, oo), s in vals:
        #     if s == root:
        #         schema.add_fluent_true_val(inst, p, oo)

        return schema
    
    def get_string(self, val=False):
        return 'not_implemented_yet'
    
    def get_schema(self):
        symbols = []
        for prec in self._precs: 
            symbols.append(precondition(prec))
        for change in self._change_pattern: 
            symbols.append(change_pattern(change)) 
        for n in self._n_used_predicates: 
            symbols.append(n_use_predicates(n))
        for n in self._n_used_static_predicates: 
            symbols.append(n_used_static_predicates(n))
        for predicate, arity in self._predicates.items(): 
            symbols.append(p_arity(predicate,arity))
        for p in self._p_used: 
            symbols.append(p_used(p))
        
        return symbols


def is_sat(string):
    if string == 'SATISFIABLE':
        return True
    if string == 'UNSATISFIABLE':
        return False
    if string == 'UNKNOWN':
        return None
    raise ValueError('Unexpected result: %s'%(string))

def parse_clingo_string(program):
    ctl = clingo.Control()
    ctl.add('base', [], program)
    ctl.ground([('base', [])])
    return list(s.symbol for s in ctl.symbolic_atoms if s.is_fact)

def parse_clingo_out(output, firstmodel=False):
    results = {}
    empty = r'\s.*?'
    answer = r'Answer: \d+?\n(.*?)\n'
    matches = re.finditer(answer, output)
    models = list(matches)
    if len(models):
        results[SAT] = True
        if firstmodel:
            text = models[0].group(1)
        else:
            text = models[-1].group(1)
        text = ''.join(w+'.' for w in text.split())
        results[SYMBOLS] = parse_clingo_string(text)
    else:
        if output.find('UNSATISFIABLE') > -1:
            results[SAT] = False
        else:
            results[SAT] = None
    if SYMBOLS not in results:
        results[SYMBOLS] = None
    models = f'Models{empty}: (.*?)\n'
    calls = f'Calls{empty}: (.*?)\n'
    time = f'Time{empty}: (.*?)s '+r'\(Solving: (.*?)s 1st Model: (.*?)s Unsat: (.*?)s\)\n'
    cputime = f'CPU Time{empty}: (.*?)s\n'
    choices = f'Choices{empty}: (\d+)'
    conflicts = f'Conflicts{empty}: (\d+)'
    rules = f'Rules{empty}: (\d+)'
    variables = f'Variables{empty}: (\d+)'
    constraints = f'Constraints{empty}: (\d+)'
    optimization = f'Models{empty}: .*?\n{empty}Optimum{empty}: (.*?)\nOptimization{empty}: (.*?)\n'
    keys_calls = [
        (models, [(MODELS, None)]),
        (calls, [(CALLS, int)]),
        (time, [(TIME, float),(SOLVING, float), (MODEL1st, float), (TIMEUNSAT, float)]),
        (cputime, [(CPUTIME, float)]),
        (choices, [(CHOICES, int)]),
        (conflicts, [(CONFLICTS, int)]),
        (rules, [(RULES, int)]),
        (variables, [(VARIABLES, int)]),
        (constraints, [(CONSTRAINTS, int)])]
    
    for regex, groups in keys_calls:
        match = re.search(regex, output)
        if match == None:
            continue
        for (key, call), value in zip(groups, match.groups()):
            results[key] = call(value) if call != None else value
    
    optmatch = re.search(optimization, output)
    if optmatch != None:
        results[OPTIMUM] = optmatch.group(1)
        results[OPTIMIZATION] = optmatch.group(2)
    else:
        results[OPTIMUM] = None
        results[OPTIMIZATION] = None
    return results

if __name__ == '__main__':
    filestr = ''.join(sys.stdin.readlines())
    clingo_result = parse_clingo_out(filestr)
    schema = STRIPSSchema.create_from_clingo(clingo_result[SYMBOLS])
    model = schema.get_schema()
    print(schema.get_string())
    for symbol in model:
        print(f'{symbol}.')

