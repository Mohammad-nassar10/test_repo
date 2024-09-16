import ast
import inspect
import tokenize

def replace_hardcoded_values(pipeline_file_path):
    """
    Analyzes a Kubeflow pipeline Python file, detects hardcoded values in component calls,
    and replaces them with pipeline input parameters.

    Args:
        pipeline_file_path: Path to the Kubeflow pipeline Python file.
    """

    with open(pipeline_file_path, 'r') as file:
        source_code = file.read()

    tree = ast.parse(source_code)
    # Collect comments using tokenize
    comments = []
    with tokenize.open(pipeline_file_path) as f:
        for tok in tokenize.generate_tokens(f.readline):
            if tok.type == tokenize.COMMENT:
                comments.append((tok.start[0], tok.string))

    class HardcodedValueReplacer(ast.NodeTransformer):
        def __init__(self):
            self.pipeline_params = set()
            self.hardcoded_values_map = {}
            self.component_names = set()
            self.pipeline_func_name = ""

        def visit_FunctionDef(self, node):
            # Collect the component functions names and the name of the pipeline function
            # print(ast.dump(node))
            for decorator in node.decorator_list:
                print(f"decorator = {decorator.attr}")
                if decorator.attr == "pipeline":
                    self.pipeline_func_name = node.name
                if decorator.attr == "component":
                    self.component_names.add(node.name)
            return self.generic_visit(node)

        def visit_Call(self, node):
            # Collect the hardcoded values from the components calls
            if isinstance(node.func, ast.Name) and node.func.id in self.component_names:
                for kwarg in node.keywords:
                    # Check if the keyword argument has a hardcoded value
                    if isinstance(kwarg.value, (ast.Constant, ast.List, ast.Dict)):
                        # Infer the parameter type based on the hardcoded value
                        if isinstance(kwarg.value, ast.Constant):
                            param_type = type(kwarg.value.value).__name__
                        elif isinstance(kwarg.value, ast.List):
                            param_type = 'list'
                        elif isinstance(kwarg.value, ast.Dict):
                            param_type = 'dict'
                        value_repr = ast.unparse(kwarg.value)  # Get a string representation of the value
                        if value_repr in self.hardcoded_values_map:
                            # Reuse existing parameter if the same value is used elsewhere
                            param_name = self.hardcoded_values_map[value_repr]
                        else:
                            param_name = f"{kwarg.arg}_param"
                            self.hardcoded_values_map[value_repr] = param_name
                            self.pipeline_params.add((param_name, param_type))

                        # Replace hardcoded value with a parameter reference
                        kwarg.value = ast.Name(id=param_name, ctx=ast.Load())
            return self.generic_visit(node)

    replacer = HardcodedValueReplacer()
    modified_tree = replacer.visit(tree)

    # Update the pipeline function's arguments
    for node in ast.walk(modified_tree):
        if isinstance(node, ast.FunctionDef) and node.name == replacer.pipeline_func_name:
            print(f"params = {replacer.pipeline_params}")
            for param_name, param_type in replacer.pipeline_params:
                # Create an argument node with type annotation (default value is not working)
                arg_node = ast.arg(arg=param_name, annotation=ast.Name(id=param_type, ctx=ast.Load()))
                node.args.args.append(arg_node)
            # ast.fix_missing_locations(node)
    # Find and update the function call to the pipeline function
    for node in ast.walk(modified_tree):
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id == replacer.pipeline_func_name:
            # node.args = []
            # Add new keyword arguments based on pipeline_params
            for param_name, _ in replacer.pipeline_params:
                node.keywords.append(ast.keyword(arg=param_name, value=ast.Name(id=param_name, ctx=ast.Load())))


    # TODO: Keep the comments from the source code
    # Convert the modified AST back to source code
    modified_source_code = ast.unparse(modified_tree)

    with open("tmp_res.py", 'w') as file:
        file.write(modified_source_code)

# Example usage
pipeline_file_path = 'store_invoices_pipeline.py'
replace_hardcoded_values(pipeline_file_path)
