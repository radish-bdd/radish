"""
EBNF Parser for radish gherkin.
"""

from pathlib import Path

from lark import (
    Lark,
    Transformer,
    v_args,
    UnexpectedInput,
    UnexpectedCharacters
)






if __name__ == "__main__":
    import sys
    tree = parse(sys.argv[1], "radish/grammer.g")
    print(tree)
