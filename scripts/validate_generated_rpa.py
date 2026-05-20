#!/usr/bin/env python3
"""Validate generated RPA Editor NextGen output before delivery."""

from __future__ import annotations

import ast
import re
import subprocess
import sys
from pathlib import Path


REQUIRED_FILES = ("readme.md", "script.py", "source.py", "main.py", "browser-handoff.json")
ASYNC_TOKENS = ("async def", "await ", "async with", "async for")
INTERACTION_METHODS = {
    "check",
    "click",
    "direct_type_text",
    "fill",
    "goto",
    "human_click",
    "human_type_text",
    "paste_text",
    "press",
    "select_option",
    "type",
    "type_text_by_random",
}
POTENTIAL_LOAD_KEYWORDS = (
    "apply",
    "confirm",
    "continue",
    "done",
    "go",
    "login",
    "next",
    "save",
    "search",
    "submit",
)
RESULT_VALUE_PATTERNS = (
    re.compile(r"expected_.*(product|title|price|asin|url|text|count|record)", re.IGNORECASE),
    re.compile(r"(observed|extracted)_.*(product|title|price|asin|url|text|count|record)", re.IGNORECASE),
)


def fail(message: str) -> None:
    print(f"generated RPA invalid: {message}", file=sys.stderr)
    raise SystemExit(1)


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8-sig")


def repo_root() -> Path:
    return Path(__file__).resolve().parents[1]


def ensure_output_dir(output_dir: Path) -> None:
    root_outputs = repo_root() / "outputs"
    resolved_output = output_dir.resolve()
    resolved_root_outputs = root_outputs.resolve()
    if not resolved_output.is_dir():
        fail(f"output directory does not exist: {output_dir}")
    if resolved_output == resolved_root_outputs:
        fail("output directory must be a task-specific subdirectory under outputs")
    try:
        resolved_output.relative_to(resolved_root_outputs)
    except ValueError:
        fail(f"output directory must be under skill root outputs: {resolved_root_outputs}")


def ensure_required_files(output_dir: Path) -> dict[str, Path]:
    paths = {name: output_dir / name for name in REQUIRED_FILES}
    missing = [name for name, path in paths.items() if not path.is_file()]
    if missing:
        fail(f"missing required files: {', '.join(missing)}")
    return paths


def parse_python(path: Path) -> ast.Module:
    try:
        return ast.parse(read_text(path), filename=str(path))
    except SyntaxError as exc:
        fail(f"{path.name} has invalid Python syntax: {exc}")


def ensure_no_async(paths: dict[str, Path]) -> None:
    for name in ("main.py", "script.py", "source.py"):
        text = read_text(paths[name])
        for token in ASYNC_TOKENS:
            if token in text:
                fail(f"{name} must not contain {token!r}")


def literal_assigned_dict(tree: ast.Module, variable_name: str, file_name: str) -> dict:
    for node in tree.body:
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id == variable_name:
                    try:
                        value = ast.literal_eval(node.value)
                    except (ValueError, TypeError):
                        fail(f"{file_name} {variable_name} must be a literal dictionary")
                    if not isinstance(value, dict):
                        fail(f"{file_name} {variable_name} must be a dictionary")
                    return value
    fail(f"{file_name} is missing {variable_name}")


def assigned_list_node(tree: ast.Module, variable_name: str, file_name: str) -> ast.List:
    for node in tree.body:
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id == variable_name:
                    if not isinstance(node.value, ast.List):
                        fail(f"{file_name} {variable_name} must be a list")
                    return node.value
    fail(f"{file_name} is missing {variable_name}")


def extract_form_names(script_tree: ast.Module) -> set[str]:
    form_names: set[str] = set()
    forms = assigned_list_node(script_tree, "SCRIPT_FORMS", "script.py")
    for index, form in enumerate(forms.elts):
        if not isinstance(form, ast.Call):
            fail(f"script.py SCRIPT_FORMS[{index}] must be a form constructor call")
        for keyword in form.keywords:
            if keyword.arg == "name" and isinstance(keyword.value, ast.Constant) and isinstance(keyword.value.value, str):
                form_names.add(keyword.value.value)
                break
        else:
            fail(f"script.py SCRIPT_FORMS[{index}] is missing a literal name")
    return form_names


def extract_source_variable_properties(source_tree: ast.Module) -> set[str]:
    properties: set[str] = set()
    for node in ast.walk(source_tree):
        if not isinstance(node, ast.FunctionDef):
            continue
        if not any(isinstance(decorator, ast.Name) and decorator.id == "property" for decorator in node.decorator_list):
            continue
        for child in ast.walk(node):
            if not isinstance(child, ast.Constant) or not isinstance(child.value, str):
                continue
            match = re.fullmatch(r"\$\{([A-Za-z_][A-Za-z0-9_.-]*)\}", child.value)
            if match:
                properties.add(match.group(1))
    return properties


def ensure_framework_contract(paths: dict[str, Path]) -> None:
    main_text = read_text(paths["main.py"])
    source_text = read_text(paths["source.py"])
    script_text = read_text(paths["script.py"])

    if "from app.core.developer.run import start_main_process_run_by_developer" not in main_text:
        fail("main.py must import start_main_process_run_by_developer from app.core.developer.run")
    if "BrowserConfig" not in main_text:
        fail("main.py must define BrowserConfig")
    if "start_main_process_run_by_developer(" not in main_text:
        fail("main.py must call start_main_process_run_by_developer")
    if "CorePageObject" not in source_text:
        fail("source.py must use CorePageObject")
    if "FormateVariableValue" not in source_text:
        fail("source.py must read runtime variables through FormateVariableValue")
    if re.search(r"\bVariableValue\b", source_text):
        fail("source.py must use FormateVariableValue, not VariableValue, for runtime variables")
    if "SCRIPT_FORMS" not in script_text or "SCRIPT_VARIABLES" not in script_text:
        fail("script.py must define SCRIPT_FORMS and SCRIPT_VARIABLES")


def ensure_runtime_guardrails(paths: dict[str, Path]) -> None:
    source_text = read_text(paths["source.py"])
    if "set_window_size_by_variable(" in source_text:
        fail("source.py must not call set_window_size_by_variable(); parse window_size and call set_window_size(width, height)")
    if re.search(r"set_window_size\(\s*\*\s*self\.window_size\s*\)", source_text):
        fail("source.py must not unpack self.window_size into set_window_size(); parse it into width and height integers first")


def call_method_name(call: ast.Call) -> str | None:
    if isinstance(call.func, ast.Attribute):
        return call.func.attr
    return None


def call_source_text(source_text: str, node: ast.AST) -> str:
    return ast.get_source_segment(source_text, node) or ""


def is_self_random_sleep_call(stmt: ast.stmt) -> bool:
    if not isinstance(stmt, ast.Expr) or not isinstance(stmt.value, ast.Call):
        return False
    call = stmt.value
    if not isinstance(call.func, ast.Attribute) or call.func.attr != "random_sleep":
        return False
    return isinstance(call.func.value, ast.Name) and call.func.value.id == "self"


def is_page_interaction_stmt(stmt: ast.stmt) -> bool:
    if not isinstance(stmt, ast.Expr) or not isinstance(stmt.value, ast.Call):
        return False
    method_name = call_method_name(stmt.value)
    return method_name in INTERACTION_METHODS


def is_page_wait_for_load_state_call(stmt: ast.stmt) -> bool:
    if not isinstance(stmt, ast.Expr) or not isinstance(stmt.value, ast.Call):
        return False
    call = stmt.value
    if not isinstance(call.func, ast.Attribute) or call.func.attr != "wait_for_load_state":
        return False
    value = call.func.value
    return (
        isinstance(value, ast.Attribute)
        and value.attr == "page"
        and isinstance(value.value, ast.Name)
        and value.value.id == "self"
    )


def iter_statement_blocks(tree: ast.AST) -> list[list[ast.stmt]]:
    blocks: list[list[ast.stmt]] = []
    for node in ast.walk(tree):
        for field_name in ("body", "orelse", "finalbody"):
            body = getattr(node, field_name, None)
            if isinstance(body, list) and body and all(isinstance(item, ast.stmt) for item in body):
                blocks.append(body)
        handlers = getattr(node, "handlers", None)
        if handlers:
            for handler in handlers:
                if handler.body:
                    blocks.append(handler.body)
    return blocks


def is_potential_load_interaction(stmt: ast.stmt, source_text: str) -> bool:
    if not isinstance(stmt, ast.Expr) or not isinstance(stmt.value, ast.Call):
        return False
    method_name = call_method_name(stmt.value)
    if method_name == "goto":
        return True
    if method_name not in {"click", "human_click", "press", "select_option"}:
        return False
    source = call_source_text(source_text, stmt).lower()
    return any(keyword in source for keyword in POTENTIAL_LOAD_KEYWORDS)


def ensure_load_state_after_potential_loads(paths: dict[str, Path]) -> None:
    source_text = read_text(paths["source.py"])
    source_tree = parse_python(paths["source.py"])
    for block in iter_statement_blocks(source_tree):
        for index, stmt in enumerate(block):
            if not is_potential_load_interaction(stmt, source_text):
                continue
            lookahead = block[index + 1 : index + 6]
            if not any(is_page_wait_for_load_state_call(candidate) for candidate in lookahead):
                method_name = call_method_name(stmt.value) if isinstance(stmt, ast.Expr) and isinstance(stmt.value, ast.Call) else "interaction"
                fail(
                    f"source.py line {getattr(stmt, 'lineno', '?')} calls {method_name} "
                    "where a page load may occur without self.page.wait_for_load_state(...) shortly after it"
                )


def ensure_random_sleep_after_interactions(paths: dict[str, Path]) -> None:
    source_tree = parse_python(paths["source.py"])
    for block in iter_statement_blocks(source_tree):
        for index, stmt in enumerate(block):
            if not is_page_interaction_stmt(stmt):
                continue
            if call_method_name(stmt.value) == "goto":
                lookahead = block[index + 1 : index + 5]
            else:
                lookahead = block[index + 1 : index + 4]
            if not any(is_self_random_sleep_call(candidate) for candidate in lookahead):
                method_name = call_method_name(stmt.value) or "interaction"
                fail(
                    f"source.py line {getattr(stmt, 'lineno', '?')} calls {method_name} "
                    "without self.random_sleep(...) shortly after it"
                )


def ensure_variable_contract(paths: dict[str, Path]) -> None:
    main_tree = parse_python(paths["main.py"])
    script_tree = parse_python(paths["script.py"])
    source_tree = parse_python(paths["source.py"])

    variable_values = literal_assigned_dict(main_tree, "VARIABLE_VALUES", "main.py")
    script_variables = literal_assigned_dict(script_tree, "SCRIPT_VARIABLES", "script.py")
    args_settings = literal_assigned_dict(source_tree, "ARGS_SETTINGS", "source.py")
    form_names = extract_form_names(script_tree)
    source_properties = extract_source_variable_properties(source_tree)

    if args_settings != {"timeout": 30000, "retry": 1}:
        fail('source.py ARGS_SETTINGS must be exactly {"timeout": 30000, "retry": 1}')

    main_names = set(variable_values)
    script_names = set(script_variables)
    if main_names != script_names:
        fail(f"main.py VARIABLE_VALUES and script.py SCRIPT_VARIABLES differ: {sorted(main_names ^ script_names)}")
    if form_names and form_names != script_names:
        fail(f"script.py SCRIPT_FORMS and SCRIPT_VARIABLES differ: {sorted(form_names ^ script_names)}")
    missing_properties = sorted(script_names - source_properties)
    if missing_properties:
        fail(f"source.py is missing FormateVariableValue properties for: {missing_properties}")

    for variable_name in sorted(script_names):
        for pattern in RESULT_VALUE_PATTERNS:
            if pattern.search(variable_name):
                fail(f"result value variable is not allowed: {variable_name}")


def ensure_handoff_valid(paths: dict[str, Path]) -> None:
    validator = repo_root() / "scripts" / "validate_browser_handoff.py"
    result = subprocess.run(
        [sys.executable, str(validator), str(paths["browser-handoff.json"])],
        cwd=str(repo_root()),
        text=True,
        capture_output=True,
    )
    if result.returncode != 0:
        message = result.stderr.strip() or result.stdout.strip() or "handoff validation failed"
        fail(message)


def ensure_py_compile(paths: dict[str, Path]) -> None:
    result = subprocess.run(
        [sys.executable, "-m", "py_compile", str(paths["main.py"]), str(paths["script.py"]), str(paths["source.py"])],
        cwd=str(repo_root()),
        text=True,
        capture_output=True,
    )
    if result.returncode != 0:
        message = result.stderr.strip() or result.stdout.strip() or "py_compile failed"
        fail(message)


def main() -> int:
    if len(sys.argv) != 2:
        print("usage: validate_generated_rpa.py <output-dir>", file=sys.stderr)
        return 2

    output_dir = Path(sys.argv[1])
    ensure_output_dir(output_dir)
    paths = ensure_required_files(output_dir)
    ensure_no_async(paths)
    ensure_framework_contract(paths)
    ensure_runtime_guardrails(paths)
    ensure_load_state_after_potential_loads(paths)
    ensure_random_sleep_after_interactions(paths)
    ensure_variable_contract(paths)
    ensure_handoff_valid(paths)
    ensure_py_compile(paths)
    print("generated RPA valid")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
