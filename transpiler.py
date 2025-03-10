import ast

class PythonToJS(ast.NodeVisitor):
    def __init__(self):
        self.js_code = []
        self.scope_stack = [set()]

    def current_scope(self):
        return self.scope_stack[-1]

    def is_defined(self, name):
        return any(name in scope for scope in reversed(self.scope_stack))

    def define_var(self, name):
        self.current_scope().add(name)

    def visit_Module(self, node):
        for stmt in node.body:
            self.visit(stmt)

    def visit_Assign(self, node):
        if len(node.targets) == 1 and isinstance(node.targets[0], ast.Name):
            target = node.targets[0].id
            value = self.convert_expr(node.value)
            if target in self.current_scope():
                self.js_code.append(f"{target} = {value};")
            elif self.is_defined(target):
                self.js_code.append(f"{target} = {value};")
            else:
                self.define_var(target)
                self.js_code.append(f"let {target} = {value};")
        else:
            self.js_code.append("  // Unsupported assignment structure")

    def visit_FunctionDef(self, node):
        args = ', '.join(arg.arg for arg in node.args.args)
        self.js_code.append(f"function {node.name}({args}) {{")
        self.scope_stack.append(set(arg.arg for arg in node.args.args))
        for stmt in node.body:
            self.visit(stmt)
        self.scope_stack.pop()
        self.js_code.append("}")

    def visit_Expr(self, node):
        if isinstance(node.value, ast.Call):
            func = node.value.func
            if isinstance(func, ast.Name):
                if func.id == 'print':
                    args = ', '.join(self.convert_expr(arg) for arg in node.value.args)
                    self.js_code.append(f"  console.log({args});")
                else:
                    args = ', '.join(self.convert_expr(arg) for arg in node.value.args)
                    self.js_code.append(f"{func.id}({args});")

    def visit_If(self, node):
        test = self.convert_expr(node.test)
        self.js_code.append(f"  if {test} {{")
        for stmt in node.body:
            self.visit(stmt)
        self.js_code.append("  } else {")
        for stmt in node.orelse:
            self.visit(stmt)
        self.js_code.append("  }")

    def convert_expr(self, node):
        if isinstance(node, ast.Constant):
            return repr(node.value)
        elif isinstance(node, ast.Name):
            return node.id
        elif isinstance(node, ast.BinOp):
            left = self.convert_expr(node.left)
            right = self.convert_expr(node.right)
            op = self.convert_operator(node.op)
            return f"({left} {op} {right})"
        elif isinstance(node, ast.BoolOp):
            op = self.convert_operator(node.op)
            values = f" {op} ".join(self.convert_expr(v) for v in node.values)
            return f"({values})"
        elif isinstance(node, ast.Compare):
            left = self.convert_expr(node.left)
            comparisons = []
            for op, comp in zip(node.ops, node.comparators):
                comparisons.append(f"{self.convert_operator(op)} {self.convert_expr(comp)}")
            return f"({left} {' '.join(comparisons)})"
        else:
            return '/* unsupported expression */'

    def convert_operator(self, op):
        operators = {
            ast.Add: '+', ast.Sub: '-', ast.Mult: '*', ast.Div: '/',
            ast.Mod: '%', ast.Pow: '**', ast.FloorDiv: '//',
            ast.And: '&&', ast.Or: '||',
            ast.Eq: '==', ast.NotEq: '!=', ast.Lt: '<', ast.LtE: '<=',
            ast.Gt: '>', ast.GtE: '>='
        }
        return operators.get(type(op), '/* unsupported op */')

    def generic_visit(self, node):
        # For unsupported nodes, just note them
        self.js_code.append(f"  // Unsupported: {type(node).__name__}")

    def transpile(self, python_code):
        tree = ast.parse(python_code)
        self.visit(tree)
        return '\n'.join(self.js_code)


if __name__ == "__main__":
    import os

    python_code = '''

x = 100
y = 5
print(x * y)

def evalNums(a, b):
    if x > y:
        print("yuhhh")
    else:
        print("nahhh")
evalNums(x, y)

x = 0
evalNums(x, y)

def printANum(num):
    x = num
    print(x)

printANum(42)

'''
    transpiler = PythonToJS()
    js_output = transpiler.transpile(python_code)

    with open("output.js", "w") as f:
        f.write(js_output)

    print("JavaScript code written to output.js")