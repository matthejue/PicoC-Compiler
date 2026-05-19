from src import global_vars

def convert_to_single_line(stmt):
    return "".join(list(map(lambda line: line.lstrip(), str(stmt).split("\n"))))
