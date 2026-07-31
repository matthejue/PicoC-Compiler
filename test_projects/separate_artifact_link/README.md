# Separate artifact linking test

This project checks that independently compiled PicoC translation units can be
linked using only their `.reti_blocks` and `.st` artifacts. It deliberately
uses nested headers, a shared struct, calls across both source-file boundaries,
per-file globals and globalized string literals. `main.picoc` contains the
project's only `main` function; its computed result is `354`.

From the repository root, compile each source independently:

```sh
./run.py -s -c test_projects/separate_artifact_link/arithmetic.picoc
./run.py -s -c test_projects/separate_artifact_link/pipeline.picoc
./run.py -s -c test_projects/separate_artifact_link/main.picoc
```

Then link only the generated artifacts:

```sh
./run.py -s \
  -o test_projects/separate_artifact_link/linked.reti \
  test_projects/separate_artifact_link/arithmetic.reti_blocks \
  test_projects/separate_artifact_link/arithmetic.st \
  test_projects/separate_artifact_link/pipeline.reti_blocks \
  test_projects/separate_artifact_link/pipeline.st \
  test_projects/separate_artifact_link/main.reti_blocks \
  test_projects/separate_artifact_link/main.st
```

The explicit `.st` arguments are optional when each matching file is beside its
`.reti_blocks` file, but they are listed to make every linker input visible.
The link creates `linked.reti` plus the usual `linked.sections` runtime-layout
sidecar; `.sections` is an output of linking, not an input to it.

For comparison, a one-shot source link can be built with:

```sh
./run.py -s \
  -o test_projects/separate_artifact_link/direct.reti \
  test_projects/separate_artifact_link/arithmetic.picoc \
  test_projects/separate_artifact_link/pipeline.picoc \
  test_projects/separate_artifact_link/main.picoc
cmp test_projects/separate_artifact_link/linked.reti \
  test_projects/separate_artifact_link/direct.reti
```
