import ast
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class Operation:
    op_type: str  # e.g. "add_column", "drop_table"
    args: list[str] = field(default_factory=list)
    kwargs: dict[str, str] = field(default_factory=dict)
    function: str = "upgrade"  # "upgrade" or "downgrade"
    source_file: str = ""


def _extract_string(node: ast.expr) -> str:
    if isinstance(node, ast.Constant) and isinstance(node.value, str):
        return node.value
    return ""


def _extract_value(node: ast.expr) -> str:
    if isinstance(node, ast.Constant):
        return str(node.value)
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Attribute):
        return f"{_extract_value(node.value)}.{node.attr}"
    return repr(ast.dump(node))


def _extract_ops_from_function(func_def: ast.FunctionDef, function_name: str) -> list[Operation]:
    ops = []
    known_ops = {
        "add_column", "drop_column", "alter_column",
        "create_table", "drop_table", "rename_table",
        "create_index", "drop_index",
    }

    for node in ast.walk(func_def):
        if not isinstance(node, ast.Call):
            continue
        # Match op.xxx() calls
        if isinstance(node.func, ast.Attribute):
            attr_name = node.func.attr
            if attr_name not in known_ops:
                continue
            # Check it's called on 'op'
            if isinstance(node.func.value, ast.Name) and node.func.value.id == "op":
                args = [_extract_string(a) or _extract_value(a) for a in node.args]
                kwargs = {}
                for kw in node.keywords:
                    if kw.arg:
                        kwargs[kw.arg] = _extract_value(kw.value)
                ops.append(Operation(
                    op_type=attr_name,
                    args=args,
                    kwargs=kwargs,
                    function=function_name,
                ))
    return ops


def is_alembic_migration(path: Path) -> bool:
    try:
        content = path.read_text()
        return "revision" in content and ("def upgrade" in content or "def downgrade" in content)
    except Exception:
        return False


def parse_migration(path: Path) -> list[Operation]:
    content = path.read_text()
    tree = ast.parse(content)
    ops = []

    for node in ast.iter_child_nodes(tree):
        if isinstance(node, ast.FunctionDef) and node.name in ("upgrade", "downgrade"):
            func_ops = _extract_ops_from_function(node, node.name)
            for op in func_ops:
                op.source_file = str(path)
            ops.extend(func_ops)

    return ops


def parse_directory(directory: Path) -> list[Operation]:
    ops = []
    for path in sorted(directory.glob("*.py")):
        if is_alembic_migration(path):
            ops.extend(parse_migration(path))
    return ops
