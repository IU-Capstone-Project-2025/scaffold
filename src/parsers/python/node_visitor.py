import ast
import pathlib
from pprint import pprint

from src.generator.graph_types import NodeType, RelationshipType
from src.parsers.python.models import CodeElement, FileGraph


def print_dict_recursive(obj, indent=1):
    if not hasattr(obj, "__dict__"):
        # print("  " * indent + repr(obj))
        return
    for key, value in obj.__dict__.items():
        # print("  " * indent + f"{key}: ", end="")
        if hasattr(value, "__dict__"):
            # print()
            pass
            # print_dict_recursive(value, indent + 1)
        elif isinstance(value, dict):
            pass
            # print()
            # print_dict_recursive_dict(value, indent + 1)
        else:
            pass
            # print(repr(value))


def print_dict_recursive_dict(d: dict, indent=0):
    for k, v in d.items():
        # print("  " * indent + f"{k}: ", end="")
        if hasattr(v, "__dict__"):
            # print()
            pass
            # print_dict_recursive(v, indent + 1)
        elif isinstance(v, dict):
            # print()
            pass
            # print_dict_recursive_dict(v, indent + 1)
        else:
            pass
            # print(repr(v))


class NodeVisitor(ast.NodeVisitor):
    def __init__(self, path):
        self.file = FileGraph(path)
        self.scope_stack: list[str] = []

    type SupportedNode = ast.ClassDef | ast.FunctionDef | ast.Call | ast.AsyncFunctionDef

    def _get_type(self, node: SupportedNode) -> NodeType:
        match node:
            case ast.ClassDef():
                return NodeType.CLASS
            case ast.FunctionDef() | ast.Call() | ast.AsyncFunctionDef():
                return NodeType.FUNCTION
            case _:
                raise Exception(f"Unexpected node: {node}")

    def _get_name(self, node: SupportedNode) -> str:
        name = None
        match node:
            case (
                ast.ClassDef(name=n)
                | ast.FunctionDef(name=n)
                | ast.AsyncFunctionDef(name=n)
            ):
                name = n
            case ast.Call(func=f):
                f: ast.expr = f
                name = getattr(f, "id", None) or getattr(f, "attr", None)
        assert name is not None, f"Name of '{node}' is not found!"
        return name

    def _create_code_element(self, node: SupportedNode) -> CodeElement:

        name = self._get_name(node)

        element = CodeElement(
            name=name,
            type=self._get_type(node),
            line_number=node.lineno,
            end_line=getattr(node, "end_lineno", node.lineno),
            docstring="",  # todo
        )
        print(__name__, 86, element)
        return element

    def visit_FunctionDef(self, node: ast.FunctionDef):
        self.scope_stack.append(node.name)

        self.file.add_element(
            self.scope_stack,
            self._create_code_element(node),
            relation_type=RelationshipType.DEFINE,
        )

        self.generic_visit(node)
        self.scope_stack.pop()

    def visit_ClassDef(self, node: ast.ClassDef):
        self.scope_stack.append(node.name)

        self.file.add_element(
            self.scope_stack,
            self._create_code_element(node),
            relation_type=RelationshipType.DEFINE,
        )

        self.generic_visit(node)
        self.scope_stack.pop()

    def visit_Call(self, node: ast.Call):
        self.scope_stack.append(self._get_name(node))

        print(__name__, 117, node.__dict__)

        self.file.add_element(
            self.scope_stack,
            self._create_code_element(node),  # todo find exist node
            relation_type=RelationshipType.USE,
        )

        self.generic_visit(node)
        self.scope_stack.pop()

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef):
        self.scope_stack.append(node.name)

        self.file.add_element(
            self.scope_stack,
            self._create_code_element(node),
            relation_type=RelationshipType.DEFINE,
        )

        self.generic_visit(node)
        self.scope_stack.pop()


if __name__ == "__main__":
    path = pathlib.Path("codebase/syntatic-1/test1.py")
    file_paths = [f for f in path.rglob("*.py") if f.is_file()]
    file_paths = [path]
    for file_path in file_paths:
        content = file_path.read_text(encoding="utf-8")
        tree = ast.parse(content, filename=str(file_path))

        v = NodeVisitor(path.name)
        v.visit(tree)
        pprint(v.file.relations)
