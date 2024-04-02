from typing import List
import clingo
import sys
import re
from utils.names import *

# create from output_vars 
# 413: get_string is missing 
# python3 incremental_solver.py --threads=64 --no_invariants --version kr21 benchmarks/match2ops_4_full_label_1r.txt --results results/ 0




CHANGE_PATTERN = ('eff', 3)
PREC_4 = ('prec', 3)
P_ARITY_2 = ('p_arity', 2)
P_USED = ('p_used', 1)
USED_PREDICATES = ('usedpredicates', 1)
USED_STATIC_PREDICATES = ('usedstaticpredicates', 1)
LABELNAME_2 = ('labelname', 2)
A_ARITY_2 = ('a_arity', 2)
UNEQUAL_2 = ('unequal', 2)
OBJ_1 = ('object', 1)

def map_to_int(symbols):
    return tuple(map(lambda x: x.number, symbols))

def map_to_number(ints):
    return tuple(map(lambda x: clingo.Number(x), ints))

def change_pattern(action, val): 
    [predicate, (p1,p2), value] = val 
    return clingo.Function('eff', [clingo.Number(action), clingo.Number(predicate), clingo.Function('', [clingo.Number(p1),clingo.Number(p2)]), clingo.Number(value)])

def precondition(action, val): 
    [predicate, (p1,p2), value] = val 
    return clingo.Function('prec', [clingo.Number(action), clingo.Number(predicate), clingo.Function('', [clingo.Number(p1),clingo.Number(p2)]), clingo.Number(value)])

def n_use_predicates(n): 
    return clingo.Function('usedpredicates', map_to_number([n]))

def n_used_static_predicates(n): 
    return clingo.Function('usedstaticpredicates', map_to_number([n]))

def p_arity(p,arity): 
    return clingo.Function('p_arity', map_to_number([p,arity]))

def p_used(p):
    return clingo.Function('p_used', map_to_number([p]))

def a_arity_2(a, arity):
    return clingo.Function('a_arity', map_to_number([a, arity]))

def unequal_2(a, args):
    return clingo.Function('unequal', [clingo.Number(a), clingo.Function('',map_to_number(args))])

def str_params(it):
    return ', '.join(('x%d' % (i) if i > 0 else 'none') for i in it)

def str_objs(it):
    return ', '.join('o%d' % (i) for i in it)


class STRIPSSchema:
    def __init__(self, root = 0):
        self._change_pattern = []
        self._precs = {}
        self._p_arity = {}
        self._p_used = set()
        self._actions = {}
        self._predicates = {}
        self._n_used_predicates = set()
        self._n_used_static_predicates = set()
        self._labels = {}
        self._effs = {}
        self._unequal = {}
        self.__objects = set()
        # self.__root = root 

    def get_root(self):
        return self.__root
    
    def set_root(self, root):
        self.__root = root

    def add_object(self, obj):
        self.__objects.add(obj)

    def get_action_arity(self, action):
        return self._actions[action]

    def set_action_arity(self, action, arity):
        self.add_action(action)
        self._actions[action] = arity


    def add_action(self, a): 
        if a not in self._actions.keys(): 
            self._actions[a] = 3 # default
        if a not in self._precs.keys(): 
            self._precs[a] = []
        if a not in self._effs.keys(): 
            self._effs[a] = []
        if a not in self._unequal.keys(): 
            self._unequal[a] = []

    def add_predicate(self, predicate):
        if predicate not in self._predicates.keys():
            self._predicates[predicate] = 2 # default

    def get_predicate_arity(self, predicate): 
        return self._predicates[predicate]

    def set_predicate_arity(self, predicate, arity):
        self.add_predicate(predicate)
        self._predicates[predicate] = arity

    def set_change_pattern(self, action, predicate, pattern, value):
        self.add_action(action)
        if action in self._effs.keys(): 
            self._effs[action].append([predicate,pattern,value])
        else: 
            self._effs[action] = [[predicate,pattern,value]]

    def set_n_used_predicates(self,p): 
        self._n_used_predicates.add(p)

    def set_n_used_static_predicates(self,p): 
        self._n_used_static_predicates.add(p)
    
    def add_used_predicate(self, p):   
        self._p_used.add(p)

    def add_uneq(self, action, args):
        self.add_action(action)
        self._unequal[action].append(args)

    def set_prec(self, action, predicate, pattern, value): 
        self.add_action(action)
        if action in self._precs.keys(): 
            self._precs[action].append([predicate,pattern,value])
        else: 
            self._precs[action] = [[predicate,pattern,value]]
        
    
    def get_label(self, action):
        return self._labels[action]

    def set_label(self, action, label):
        self.add_action(action)
        self._labels[action] = label

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
                action, predicate, v = symbol.arguments
                pred, numbers = predicate.arguments
                p1,p2 = numbers.arguments
                schema.set_prec(action.number, pred.number, (p1.number,p2.number) ,v.number) 
            elif symbol.match(*P_USED): 
                p, = symbol.arguments
                schema.add_used_predicate(p.number)
            elif symbol.match(*CHANGE_PATTERN): 
                action, predicate, v = symbol.arguments
                pred, numbers = predicate.arguments
                p1,p2 = numbers.arguments
                schema.set_change_pattern(action.number, pred.number, (p1.number,p2.number) ,v.number) 
            elif symbol.match(*USED_PREDICATES): 
                n, = symbol.arguments
                schema.set_n_used_predicates(n.number) 
            elif symbol.match(*USED_STATIC_PREDICATES): 
                n, = symbol.arguments
                schema.set_n_used_static_predicates(n.number)
            elif symbol.match(*LABELNAME_2):
                a, l = symbol.arguments
                schema.set_label(a.number, str(l)) 
            elif symbol.match(*UNEQUAL_2):
                a, args = symbol.arguments
                schema.add_uneq(a.number, map_to_int(args.arguments))
            elif symbol.match(*OBJ_1):
                o, = symbol.arguments
                schema.add_object(o.number)
            



        # root = schema.get_root()
        # for inst, (p, oo), s in vals:
        #     if s == root:
        #         schema.add_fluent_true_val(inst, p, oo)

        return schema
    

    def get_string_action(self, action):
        
        out = ''
        out += '\ta%s(%s) ' % (action, str_params(range(1,self.get_action_arity(action)+1)))
        label = self.get_label(action)
        if label != None:
            out += 'label %s' % (label)
        out += '\n'
        str_stat = []
        str_fluent = []

        for args in self._unequal[action]:
            str_stat.append('neq(%s)' % str_params(args))
        
        for p, args, val in self._precs[action]:
            sign = '' if val else '-'
            arity = self.get_predicate_arity(p)
            str_fluent.append(sign + 'p%s(%s)' % (p, str_params(args[:arity])))
        out += '\t\tStatic: %s\n' % (', '.join(str_stat))
        out += '\t\tPre: %s\n' % (', '.join(str_fluent))
        str_eff = []
        for p, args, val in self._effs[action]:
            sign = '' if val else '-'
            arity = self.get_predicate_arity(p)
            str_eff.append(sign + 'p%s(%s)' % (p, str_params(args[:arity])))
        out += '\t\tEff: %s\n' % (', '.join(str_eff))
        return out    


    #### 

    def get_string(self, val=False):
        out = ''
        
        out += 'Fluent Predicates:\n'
        
        used_predicates = list(self._p_used)
        used_predicates.sort()
        
        n = list(self._n_used_predicates)[0]

        for p in used_predicates: 
            arity = self.get_predicate_arity(p)
            out += '\tp%s(%s)\n' % (p, str_params(range(1,arity+1)))
            
            n -= 1

            if n == 0: 
                out += 'Static Predicates:\n'
        out += 'Actions:\n'
        print(self._actions)
        for a in sorted(self._actions):
            out += self.get_string_action(a)
        out += 'Objects: %s\n' % (', '.join('o%d' % (o) for o in sorted(self.__objects)))
        return out
    

    ###########



    def get_schema(self):
        symbols = []
        for action, prec in self._precs.items():
            for pre in prec: 
                symbols.append(precondition(action, pre))
        for action, effs in self._effs.items(): 
            for eff in effs: 
                symbols.append(change_pattern(action,eff)) 
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

