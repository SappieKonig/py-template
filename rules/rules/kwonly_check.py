import ast
import sys
from pathlib import Path
from typing import Iterable
import textwrap

EXCLUDE = {".git", ".venv", "build", "dist", "node_modules"}

def iter_py_files(paths: Iterable[str]) -> Iterable[Path]:
    roots = [Path(p) for p in (paths or ["."])]
    for r in roots:
        if r.is_dir():
            for f in r.rglob("*.py"):
                if any(part in EXCLUDE for part in f.parts):
                    continue
                yield f
        elif r.suffix == ".py":
            yield r

def _violations_for_source(src: str, filename: str) -> list[tuple[int, int, str]]:
    try:
        tree = ast.parse(src, filename=filename)
    except SyntaxError:
        return []
    lines = src.splitlines()
    out: list[tuple[int, int, str]] = []

    class V(ast.NodeVisitor):
        def visit_FunctionDef(self, n: ast.FunctionDef) -> None:
            if "kwonly: ignore" in lines[n.lineno - 1]:
                return
            a = n.args
            pos_params = a.posonlyargs + a.args  # parameters passable positionally
            if a.defaults and pos_params:
                first_defaulted = pos_params[-len(a.defaults):][0]
                out.append((
                    first_defaulted.lineno,
                    first_defaulted.col_offset + 1,
                    "KWONLY001 defaulted parameter must be keyword-only; "
                    "insert '*' before the first defaulted parameter",
                ))
            self.generic_visit(n)

        visit_AsyncFunctionDef = visit_FunctionDef  # type: ignore

    V().visit(tree)
    return out

def check_path(path: Path) -> list[str]:
    try:
        src = path.read_text(encoding="utf-8")
    except Exception:
        return []
    issues = _violations_for_source(src, str(path))
    return [f"{path}:{ln}:{col}: {msg}" for (ln, col, msg) in issues]

def check_source(src: str) -> list[str]:
    """Helper used by tests (accepts indented triple-quoted snippets)."""
    src = textwrap.dedent(src).lstrip("\n")
    return [f"<memory>:{ln}:{col}: {msg}"
            for (ln, col, msg) in _violations_for_source(src, "<memory>")]

def main(argv: list[str] | None = None) -> int:
    argv = argv or sys.argv
    code = 0
    for f in iter_py_files(argv[1:]):
        for line in check_path(f):
            print(line)
            code = 1
    return code
