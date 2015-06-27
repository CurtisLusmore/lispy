def tokenize(chars):
    """Convert a string of characters into a list of tokens."""
    return chars.replace('(', ' ( ').replace(')', ' ) ').split()

def parse(program):
    """Read a Scheme expression from a string."""
    return read_from_tokens(tokenize(program))

def read_from_tokens(tokens):
    """Read an expression from a sequence of tokens."""
    if len(tokens) == 0:
        raise SyntaxError("Unexpected EOF while reading.")

    token = tokens.pop(0)

    if token is '(':
        L = []
        while tokens[0] is not ')':
            L.append(read_from_tokens(tokens))
        tokens.pop(0) # pop off ')'
        return L

    elif token is ')':
        raise SyntaxError("Unexpected ')' while reading.")

    else:
        return atom(token)

def atom(token):
    """Numbers become numbers; every other token is a symbol."""
    try:
        return int(token)

    except ValueError:
        try:
            return float(token)

        except ValueError:
            return Symbol(token)

Symbol = str
List = list
Number = (int, float)

class Procedure:
    """A user-defined Scheme procedure."""
    def __init__(self, parms, body, env):
        self.parms = parms
        self.body = body
        self.env = env

    def __call__(self, *args):
        return eval(self.body, Env(self.parms, args, self.env))

class Env(dict):
    """An environment: a dict of {'var': val} pairs, with an outer Env."""
    def __init__(self, parms=(), args=(), outer=None):
        self.update(zip(parms, args))
        self.outer = outer

    def find(self, var):
        """Find the innermost Env where var appears."""
        return self if (var in self) else self.outer.find(var)

def standard_env():
    """An environment with some Scheme standard procedures."""
    import math
    import operator as op

    env = Env()
    env.update(vars(math))
    env.update({
        '+': op.add, '-': op.sub, '*': op.mul, '/': op.truediv,
        '>': op.gt, '<': op.lt, '>=': op.ge, '<=': op.le, '=': op.eq,

        'abs': abs,
        'max': max,
        'min': min,
        'round': round,

        'begin': lambda *x: x[-1],
        'call': lambda f, a: f(*a),

        'head': lambda x: x[0],
        'tail': lambda x: x[1:],
        'pair': lambda x, y: [x] + y,
        'list': lambda *x: list(x),
        'length': len,
        'append': op.add,
        'map': map,

        'eq?': op.is_,
        'equal?': op.eq,
        'func?': callable,
        'list?': lambda x: isinstance(x, List),
        'null?': lambda x: x is [],
        'number?': lambda x: isinstance(x, Number),
        'symbol?': lambda x: isinstance(x, Symbol),
        'not': op.not_,
    })
    return env

global_env = standard_env()

def eval(expr, env=global_env):
    """Evaluate an expression in an environment."""
    if isinstance(expr, Symbol):
        return env.find(expr)[expr]

    if not isinstance(expr, List):
        return expr

    op, *args = expr

    if op == 'quote':
        return args

    if op == 'if':
        (cond, branch_t, branch_f) = args
        branch = branch_t if eval(cond, env) else branch_f
        return eval(branch, env)

    if op == 'defn':
        (var, expr) = args
        env[var] = eval(expr, env)
        return

    if op == "set!":
        (var, expr) = args
        env.find(var)[var] = eval(expr, env)
        return

    if op == "func":
        (parms, body) = args
        return Procedure(parms, body, env)

    proc = eval(op, env)
    args = [eval(arg, env) for arg in args]
    return proc(*args)

def repl(prompt='lis.py> '):
    """A read-eval-print loop."""
    while True:
        try:
            program = input(prompt)
        except EOFError:
            break

        val = eval(parse(program))
        if val is not None:
            print(schemestr(val))

def schemestr(expr):
    """Converts a Python object back into a Scheme-readable string."""
    if isinstance(expr, list):
        return '(' + ' '.join(map(schemestr, expr)) + ')'
    else:
        return str(expr)

if __name__ == '__main__':
    repl()
