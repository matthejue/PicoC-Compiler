import ast

def build_ast_from_string(expr_str, node_classes):
    """
    Parse a string like "BinOp(Num('2'), Mul('*'), Num('1'))"
    into actual nested ASTNode objects.
    
    Args:
        expr_str (str): The input string representation.
        node_classes (dict): Mapping of class names to class objects.
    
    Returns:
        ASTNode: The root node of the parsed tree.
    """
    tree = ast.parse(expr_str, mode='eval')
    return _instantiate_node(tree.body, node_classes)


def _instantiate_node(node, node_classes):
    if isinstance(node, ast.Call):
        class_name = node.func.id  # e.g., 'BinOp'
        if class_name not in node_classes:
            raise ValueError(f"Unknown node class: {class_name}")
        cls = node_classes[class_name]
        args = [_instantiate_node(arg, node_classes) for arg in node.args]
        return cls(*args)

    elif isinstance(node, ast.List):
        return [_instantiate_node(elt, node_classes) for elt in node.elts]
    
    elif isinstance(node, ast.Constant):
        return node.value
    
    elif isinstance(node, ast.Name):
        # Handle bare names if needed
        return node.id
    
    else:
        raise TypeError(f"Unsupported AST node type: {type(node).__name__}")
