import ast
import tokenize
import io
from pathlib import Path

class PythonToJS(ast.NodeVisitor):
    def __init__(self, comments=None):
        self.js_code = []
        self.indent_level = 0
        self.scope_stack = [set()]
        self.comments = comments or {}
        self.last_lineno = 0

    def emit(self, line=""):
        self.js_code.append("  " * self.indent_level + line)

    def emit_blank_line(self):
        self.js_code.append("")

    def current_scope(self):
        return self.scope_stack[-1]

    def is_defined_local(self, name):
        return name in self.current_scope()

    def is_defined_anywhere(self, name):
        return any(name in scope for scope in reversed(self.scope_stack))

    def define_var(self, name):
        self.current_scope().add(name)

    def visit(self, node):
        lineno = getattr(node, 'lineno', None)
        if lineno:
            for i in range(self.last_lineno + 1, lineno + 1):
                if i in self.comments:
                    for comment in self.comments[i]:
                        self.emit(f"// {comment.strip()}")
        self.last_lineno = lineno or self.last_lineno
        super().visit(node)

    def visit_Module(self, node):
        for i, stmt in enumerate(node.body):
            self.visit(stmt)
            if i + 1 < len(node.body):
                self.emit_blank_line()

    def visit_Assign(self, node):
        if len(node.targets) == 1 and isinstance(node.targets[0], ast.Name):
            target = node.targets[0].id
            value = self.convert_expr(node.value)
            if self.is_defined_local(target):
                self.emit(f"{target} = {value};")
            elif self.is_defined_anywhere(target):
                if len(self.scope_stack) > 1:
                    self.define_var(target)
                    self.emit(f"let {target} = {value};")
                else:
                    self.emit(f"{target} = {value};")
            else:
                self.define_var(target)
                self.emit(f"let {target} = {value};")
        else:
            self.emit("// Unsupported assignment structure")

    def visit_FunctionDef(self, node):
        args = ', '.join(arg.arg for arg in node.args.args)
        self.emit(f"function {node.name}({args}) {{")
        self.indent_level += 1
        self.scope_stack.append(set(arg.arg for arg in node.args.args))
        for stmt in node.body:
            self.visit(stmt)
        self.scope_stack.pop()
        self.indent_level -= 1
        self.emit("}")

    def visit_Return(self, node):
        value = self.convert_expr(node.value)
        self.emit(f"return {value};")

    def visit_Expr(self, node):
        if isinstance(node.value, ast.Call):
            func = node.value.func
            if isinstance(func, ast.Name):
                if func.id == 'print':
                    args = ', '.join(self.convert_expr(arg) for arg in node.value.args)
                    self.emit(f"console.log({args});")
                else:
                    args = ', '.join(self.convert_expr(arg) for arg in node.value.args)
                    self.emit(f"{func.id}({args});")
        elif isinstance(node.value, ast.Constant) and isinstance(node.value.value, str):
            comment_text = node.value.value.strip()
            if "\n" in comment_text:
                self.emit("/*")
                for line in comment_text.splitlines():
                    self.emit(f" * {line.strip()}")
                self.emit(" */")
            else:
                self.emit(f"// {comment_text}")

    def visit_If(self, node):
        test = self.convert_expr(node.test)
        self.emit(f"if {test} {{")
        self.indent_level += 1
        for stmt in node.body:
            self.visit(stmt)
        self.indent_level -= 1
        self.emit("} else {")
        self.indent_level += 1
        for stmt in node.orelse:
            self.visit(stmt)
        self.indent_level -= 1
        self.emit("}")

    def visit_For(self, node):
        target = self.convert_expr(node.target)
        iter_ = self.convert_expr(node.iter)
        self.emit(f"for (let {target} of {iter_}) {{")
        self.indent_level += 1
        self.scope_stack.append(set())
        for stmt in node.body:
            self.visit(stmt)
        self.scope_stack.pop()
        self.indent_level -= 1
        self.emit("}")

    def visit_While(self, node):
        test = self.convert_expr(node.test)
        self.emit(f"while {test} {{")
        self.indent_level += 1
        for stmt in node.body:
            self.visit(stmt)
        self.indent_level -= 1
        self.emit("}")

    def visit_Match(self, node):
        subject = self.convert_expr(node.subject)
        self.emit(f"switch ({subject}) {{")
        self.indent_level += 1
        for case in node.cases:
            pattern_str = self.convert_pattern(case.pattern)
            if pattern_str == "default":
                self.emit("default:")
            else:
                self.emit(f"case {pattern_str}:")
            self.indent_level += 1
            for stmt in case.body:
                self.visit(stmt)
            self.emit("break;")
            self.indent_level -= 1
        self.indent_level -= 1
        self.emit("}")

    def convert_pattern(self, pattern):
        if isinstance(pattern, ast.MatchValue):
            return self.convert_expr(pattern.value)
        elif isinstance(pattern, ast.MatchSingleton):
            return str(pattern.value)
        elif isinstance(pattern, ast.MatchAs) and pattern.name is None:
            return "default"
        else:
            return '/* unsupported pattern */'

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
        elif isinstance(node, ast.Call):
            func = self.convert_expr(node.func)
            args = ', '.join(self.convert_expr(arg) for arg in node.args)
            return f"{func}({args})"
        elif isinstance(node, ast.List):
            return '[' + ', '.join(self.convert_expr(e) for e in node.elts) + ']'
        elif isinstance(node, ast.Tuple):
            return '[' + ', '.join(self.convert_expr(e) for e in node.elts) + ']'
        elif isinstance(node, ast.Set):
            return f"new Set([{', '.join(self.convert_expr(e) for e in node.elts)}])"
        elif isinstance(node, ast.Dict):
            keys = [self.convert_expr(k) for k in node.keys]
            values = [self.convert_expr(v) for v in node.values]
            return '{' + ', '.join(f"{k}: {v}" for k, v in zip(keys, values)) + '}'
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
        self.emit(f"// Unsupported: {type(node).__name__}")

    def transpile(self, python_code):
        self.js_code = []
        self.indent_level = 0
        self.last_lineno = 0
        tree = ast.parse(python_code)
        self.visit(tree)
        return '\n'.join(self.js_code)

def extract_comments(source_code):
    comments = {}
    tokens = tokenize.generate_tokens(io.StringIO(source_code).readline)
    for tok_type, tok_string, start, _, _ in tokens:
        if tok_type == tokenize.COMMENT:
            lineno = start[0]
            comments.setdefault(lineno, []).append(tok_string[1:].strip())
    return comments

if __name__ == "__main__":
    PROJECT_DIR = Path(__file__).parent
    input_file = PROJECT_DIR / "input.py"

    if not input_file.exists():
        print(f"Error: '{input_file}' not found in the current directory.")
    else:
        with open(input_file, "r") as f:
            python_code = f.read()

        comments = extract_comments(python_code)
        transpiler = PythonToJS(comments)
        js_output = transpiler.transpile(python_code)

        with open("output.js", "w") as f:
            f.write(js_output)

        print("JavaScript code written to output.js")