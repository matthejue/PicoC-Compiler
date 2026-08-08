set -eu

tree-sitter generate
python ../../scripts/build_tree_sitter.py tree-sitter-reti
