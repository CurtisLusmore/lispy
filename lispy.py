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
Env = dict

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
        'append': op.add,
        'apply': lambda f, a: f(*a),
        'begin': lambda *x: x[-1],
        'car': lambda x: x[0],
        'cdr': lambda x: x[1:],
        'cons': lambda x, y: [x] + y,
        'eq?': op.is_,
        'equal?': op.eq,
        'length': len,
        'list': lambda *x: list(x),
        'list?': lambda x: isinstance(x, List),
        'map': map,
        'max': max,
        'min': min,
        'not': op.not_,
        'null?': lambda x: x is [],
        'number?': lambda x: isinstance(x, Number),
        'procedure?': callable,
        'round': round,
        'symbol?': lambda x: isinstance(x, Symbol),
    })
    return env

global_env = standard_env()

def eval(x, env=global_env):
    """Evaluate an expression in an environment."""
    if isinstance(x, Symbol):
        return env[x]

    if not isinstance(x, List):
        return x

    op, *args = x

    if op == 'quote':
        return args

    if op == 'if':
        (cond, branch_t, branch_f) = args
        branch = branch_t if eval(cond, env) else branch_f
        return eval(branch, env)

    if op == 'define':
        (var, expr) = args
        env[var] = eval(expr, env)
        return

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
