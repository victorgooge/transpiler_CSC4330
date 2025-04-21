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
        self.BIN_OP_PRECEDENCE = {
            ast.Pow: 15,
            ast.Mult: 14, ast.MatMult: 14, ast.Div: 14, ast.FloorDiv: 14, ast.Mod: 14,
            ast.Add: 13, ast.Sub: 13,
            ast.LShift: 12, ast.RShift: 12,
            ast.BitAnd: 11,
            ast.BitXor: 10,
            ast.BitOr: 9,
            ast.Eq: 8, ast.NotEq: 8, ast.Lt: 8, ast.LtE: 8, ast.Gt: 8, ast.GtE: 8,
            ast.Is: 8, ast.IsNot: 8, ast.In: 8, ast.NotIn: 8,
            ast.And: 6,
            ast.Or: 5
        }

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
        if len(node.targets) == 1:
            if isinstance(node.targets[0], ast.Name):
                target = node.targets[0].id
                value = self.convert_expr(node.value)
                if not self.is_defined_local(target):
                    self.define_var(target)
                    self.emit(f"let {target} = {value};")
                else:
                    self.emit(f"{target} = {value};")
            elif isinstance(node.targets[0], ast.Tuple):
                # Handle tuple unpacking
                value = self.convert_expr(node.value)
                for i, target in enumerate(node.targets[0].elts):
                    if isinstance(target, ast.Name):
                        if not self.is_defined_anywhere(target.id):
                            self.define_var(target.id)
                            self.emit(f"let {target.id} = {value}[{i}];")
                        else:
                            self.emit(f"{target.id} = {value}[{i}];")
            elif isinstance(node.targets[0], ast.Subscript):
                target = self.convert_expr(node.targets[0])
                value = self.convert_expr(node.value)
                self.emit(f"{target} = {value};")
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
        current = node
        first = True

        while True:
            test = self.convert_expr(current.test)
            if first:
                self.emit(f"if ({test}) {{")
                first = False
            else:
                self.emit(f"}} else if ({test}) {{")

            self.indent_level += 1
            for stmt in current.body:
                self.visit(stmt)
            self.indent_level -= 1

            # Handle elif chains
            if len(current.orelse) == 1 and isinstance(current.orelse[0], ast.If):
                current = current.orelse[0]
            else:
                break

        # Handle final else (if any)
        if current.orelse:
            self.emit("} else {")
            self.indent_level += 1
            for stmt in current.orelse:
                self.visit(stmt)
            self.indent_level -= 1
            self.emit("}")
        else:
            self.emit("}")

    def visit_For(self, node):
        # Check for range(...)
        if (
            isinstance(node.iter, ast.Call)
            and isinstance(node.iter.func, ast.Name)
            and node.iter.func.id == 'range'
        ):
            args = node.iter.args
            target = self.convert_expr(node.target)

            if len(args) == 1:
                stop = self.convert_expr(args[0])
                self.emit(f"for (let {target} = 0; {target} < {stop}; {target}++) {{")
            elif len(args) == 2:
                start = self.convert_expr(args[0])
                stop = self.convert_expr(args[1])
                self.emit(f"for (let {target} = {start}; {target} < {stop}; {target}++) {{")
            elif len(args) == 3:
                start = self.convert_expr(args[0])
                stop = self.convert_expr(args[1])
                step = self.convert_expr(args[2])
                self.emit(f"for (let {target} = {start}; {step} > 0 ? {target} < {stop} : {target} > {stop}; {target} += {step}) {{")
            else:
                self.emit(f"// Unsupported range with {len(args)} args")
                return
        else:
            # fallback to: for x in iterable
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

    def visit_Break(self, node):
        self.emit("break;")

    def visit_Continue(self, node):
        self.emit("continue;")

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
            if node.value is None:
                return "null"
            elif isinstance(node.value, bool):
                return str(node.value).lower()
            return repr(node.value)
        elif isinstance(node, ast.Name):
            if node.id == 'len':
                return '/* len */'  
            elif node.id == 'range':
                return '/* range */'  
            return node.id
        
        elif isinstance(node, ast.BinOp):
            op_type = type(node.op)
            op_str = self.convert_operator(node.op)

            def wrap(expr, inner_node):
                if isinstance(inner_node, ast.BinOp):
                    inner_prec = self.BIN_OP_PRECEDENCE.get(type(inner_node.op), 0)
                    outer_prec = self.BIN_OP_PRECEDENCE.get(op_type, 0)
                    if inner_prec < outer_prec:
                        return f"({expr})"
                return expr

            left = wrap(self.convert_expr(node.left), node.left)
            right = wrap(self.convert_expr(node.right), node.right)

            if isinstance(node.op, ast.FloorDiv):
                return f"Math.floor({left} / {right})"
            return f"{left} {op_str} {right}"


        
        elif isinstance(node, ast.BoolOp):
            op = self.convert_operator(node.op)
            parts = []
            for v in node.values:
                expr = self.convert_expr(v)
                # Only wrap if it's not a simple literal or name
                if isinstance(v, (ast.Constant, ast.Name, ast.UnaryOp)):
                    parts.append(expr)
                else:
                    parts.append(f"({expr})")
            return f"{f' {op} '.join(parts)}"

        elif isinstance(node, ast.Compare):
            left = self.convert_expr(node.left)
            comparisons = []
            for op, comp in zip(node.ops, node.comparators):
                comparisons.append(f"{self.convert_operator(op)} {self.convert_expr(comp)}")
            
            # Only wrap if there are multiple comparisons (Python allows chaining: a < b < c)
            comparison_str = f"{left} {' '.join(comparisons)}"
            if len(node.ops) > 1:
                return f"({comparison_str})"
            return comparison_str

        elif isinstance(node, ast.Call):
            func = self.convert_expr(node.func)
            args = [self.convert_expr(arg) for arg in node.args]
            
            if func == '/* len */':
                if args:
                    return f"{args[0]}.length"
                return '0'
            
            elif func == '/* range */':
                if len(args) == 1:
                    return f"Array.from({{length: {args[0]}}}).map((_, i) => i)"
                elif len(args) == 2:
                    return f"Array.from({{length: {args[1]} - {args[0]}}}).map((_, i) => i + {args[0]})"
                elif len(args) == 3:
                    return f"Array.from({{length: Math.floor(({args[1]} - {args[0]}) / {args[2]})}}).map((_, i) => i * {args[2]} + {args[0]})"
                return '[]'
            
            return f"{func}({', '.join(args)})"
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
        elif isinstance(node, ast.JoinedStr):
            parts = []
            for value in node.values:
                if isinstance(value, ast.Constant):
                    parts.append(value.value)
                elif isinstance(value, ast.FormattedValue):
                    expr = self.convert_expr(value.value)
                    if value.format_spec:
                        if '.2f' in str(value.format_spec):
                            expr = f"{expr}.toFixed(2)"
                    parts.append(f"${{{expr}}}")
            return f"`{''.join(parts)}`"
        elif isinstance(node, ast.Attribute):
            value = self.convert_expr(node.value)
            method_map = {
                'append': 'push',
                'extend': 'push',
                'remove': 'splice',
                'pop': 'pop',
                'clear': 'length = 0',
                'index': 'indexOf',
                'count': 'filter(x => x ===).length',
                'sort': 'sort',
                'reverse': 'reverse',
            }
            attr = method_map.get(node.attr, node.attr)
            return f"{value}.{attr}"
        elif isinstance(node, ast.ListComp):
            return self.visit_ListComp(node)
        elif isinstance(node, ast.Subscript):
            value = self.convert_expr(node.value)
            if isinstance(node.slice, ast.Index):
                index = self.convert_expr(node.slice.value)
            else:
                index = self.convert_expr(node.slice)
            return f"{value}[{index}]"
        elif isinstance(node, ast.UnaryOp):
            op = self.convert_operator(node.op)
            operand = self.convert_expr(node.operand)
            if isinstance(node.op, ast.Not):
                return f"(!{operand})"
            return f"{op}{operand}"
        else:
            return '/* unsupported expression */'

    def convert_operator(self, op):
        operators = {
            ast.Add: '+', ast.Sub: '-', ast.Mult: '*', ast.Div: '/',
            ast.Mod: '%', ast.Pow: '**',
            ast.And: '&&', ast.Or: '||',
            ast.Eq: '==', ast.NotEq: '!=', ast.Lt: '<', ast.LtE: '<=',
            ast.Gt: '>', ast.GtE: '>=',
            ast.Not: '!', ast.USub: '-', ast.UAdd: '+'
        }
        return operators.get(type(op), '/* unsupported op */')

    def visit_AugAssign(self, node):
        target = self.convert_expr(node.target)
        value = self.convert_expr(node.value)
        op = self.convert_operator(node.op)
        self.emit(f"{target} {op}= {value};")

    def visit_Attribute(self, node):
        value = self.convert_expr(node.value)
        return f"{value}.{node.attr}"

    def visit_ListComp(self, node):
        elt = self.convert_expr(node.elt)
        generators = node.generators[0]  
        target = self.convert_expr(generators.target)
        iter_expr = self.convert_expr(generators.iter)
        
        filters = []
        for if_clause in generators.ifs:
            filters.append(self.convert_expr(if_clause))
        
        if isinstance(generators.iter, ast.Call) and isinstance(generators.iter.func, ast.Name) and generators.iter.func.id == 'range':
            if len(generators.iter.args) == 1:
                end = self.convert_expr(generators.iter.args[0])
                array_expr = f"Array.from({{length: {end}}}).map((_, {target}) => {elt})"
            else:
                self.emit("// Range with start/step not fully supported")
                array_expr = "[]"
        else:
            array_expr = f"Array.from({iter_expr}).map({target} => {elt})"
        
        for filter_expr in filters:
            array_expr += f".filter({target} => {filter_expr})"
        
        return array_expr

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