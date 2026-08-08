def log(identifier_name, identifier_value):
    with open("/tmp/picoc_compiler/log.txt", "a") as log_file:
        log_file.write(f"{identifier_name}: {identifier_value}\n")
