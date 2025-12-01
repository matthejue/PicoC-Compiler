from src import global_vars

def convert_to_single_line(stmt):
    # tmp = global_vars.args.double_verbose
    # global_vars.args.double_verbose = True
    single_line = "".join(list(map(lambda line: line.lstrip(), str(stmt).split("\n"))))
    # global_vars.args.double_verbose = tmp
    return single_line
