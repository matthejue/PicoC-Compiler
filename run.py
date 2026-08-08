#!/home/areo/Documents/Studium/PicoC-Compiler/.virtualenv/bin/python
from source.main import main

if __name__ == "__main__":
    main()

# from source.test import build_ast_from_string
# # from source.picoc_nodes import Name, Num, BinOp, Mul
# from source import global_vars
# import inspect
# import source.picoc_nodes as picoc_nodes
#
# if __name__ == "__main__":
#     class ARGS:
#         double_verbose = True
#
#     global_vars.args = ARGS()
#
#     global_vars.args.double_verbose = False
#
# # Automatically collect all classes defined in source.picoc_nodes
#     node_classes = {
#         name: cls
#         for name, cls in inspect.getmembers(picoc_nodes, inspect.isclass)
#         # Optional: only include classes actually defined in this module
#         if cls.__module__ == picoc_nodes.__name__
#     }
#
#     # node_classes = {"Name": Name, "Num": Num, "BinOp": BinOp, "Mul": Mul}
#
#     # expr = "BinOp(Num('2'), Mul('*'), Num('1'))"
#     expr = "FunDecl(IntType(), Name('compute'), [Alloc(Writeable(), IntType(), Name('x'))])"
#     tree = build_ast_from_string(expr, node_classes)
#     print(tree)
