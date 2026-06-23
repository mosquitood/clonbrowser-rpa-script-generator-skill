#!/usr/bin/env python3
"""Validate generated RPA Editor NextGen output before delivery."""

from __future__ import annotations

import ast
import argparse
import os
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
ORIGINAL_PROMPT_HEADING = "## Original Codex Skill Prompt"


def fail(message: str) -> None:
    print(f"generated RPA invalid: {message}", file=sys.stderr)
    raise SystemExit(1)


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8-sig")


def repo_root() -> Path:
    return Path(__file__).resolve().parents[1]


def ensure_output_dir(output_dir: Path) -> None:
    fail("validate_generated_rpa.py requires --debug-root; output_dir must be the confirmed script input directory")


def relative_to_root(path: Path, root: Path, label: str) -> Path:
    try:
        return path.resolve().relative_to(root.resolve())
    except ValueError:
        fail(f"{label} must be under debug root: {root.resolve()}")


def ensure_debug_output_dir(output_dir: Path, debug_root: Path) -> Path:
    resolved_output = output_dir.resolve()
    resolved_debug_root = debug_root.resolve()
    if not resolved_debug_root.is_dir():
        fail(f"debug root directory does not exist: {debug_root}")
    if not resolved_output.is_dir():
        fail(f"output directory does not exist: {output_dir}")
    if resolved_output == resolved_debug_root:
        fail("script input directory must be a child directory under debug root")

    relative_output = relative_to_root(output_dir, debug_root, "output directory")
    if not relative_output.parts:
        fail("script input directory must be a child directory under debug root")
    invalid_parts = [part for part in relative_output.parts if not part.isidentifier()]
    if invalid_parts:
        fail(
            "debug script input directory must be importable as Python package parts; "
            f"invalid path parts: {invalid_parts}"
        )
    return relative_output


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


def ensure_readme_prompt_contract(paths: dict[str, Path]) -> None:
    readme_text = read_text(paths["readme.md"])
    heading_index = readme_text.find(ORIGINAL_PROMPT_HEADING)
    if heading_index == -1:
        fail(f"readme.md must include a {ORIGINAL_PROMPT_HEADING!r} section with the full Codex skill prompt")

    section_body = readme_text[heading_index + len(ORIGINAL_PROMPT_HEADING) :]
    next_heading = re.search(r"(?m)^##\s+", section_body)
    if next_heading:
        section_body = section_body[: next_heading.start()]
    if not section_body.strip():
        fail(f"readme.md {ORIGINAL_PROMPT_HEADING!r} section must not be empty")


def browser_config_values(main_tree: ast.Module) -> tuple[str | None, str | None]:
    for node in ast.walk(main_tree):
        if not isinstance(node, ast.Call):
            continue
        func = node.func
        if not isinstance(func, ast.Name) or func.id != "BrowserConfig":
            continue
        values: dict[str, str] = {}
        for keyword in node.keywords:
            if keyword.arg in {"platform", "id"} and isinstance(keyword.value, ast.Constant):
                if isinstance(keyword.value.value, str):
                    values[keyword.arg] = keyword.value.value
        return values.get("platform"), values.get("id")
    return None, None


def ensure_browser_config_contract(paths: dict[str, Path]) -> None:
    main_tree = parse_python(paths["main.py"])
    platform, browser_id = browser_config_values(main_tree)
    if not platform or not platform.strip():
        fail("main.py BrowserConfig.platform must be a non-empty literal string from the confirmed RPA runtime")
    if not browser_id or not browser_id.strip():
        fail("main.py BrowserConfig.id must be a non-empty literal string from the confirmed RPA runtime")


def ensure_debug_import_contract(paths: dict[str, Path], relative_output: Path) -> None:
    main_tree = parse_python(paths["main.py"])
    expected_module = ".".join(relative_output.parts) + ".source"
    source_imports = [
        node.module
        for node in ast.walk(main_tree)
        if isinstance(node, ast.ImportFrom) and node.module and node.module.endswith(".source")
    ]
    if expected_module not in source_imports:
        fail(
            "main.py source import must be derived from the script input directory relative to debug root; "
            f"expected from {expected_module} import <PageClassName>, found {source_imports or 'none'}"
        )


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


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Validate generated RPA Editor NextGen output before delivery.")
    parser.add_argument(
        "output_dir",
        nargs="?",
        help="Generated script output directory. In debug mode, this is the script input directory. Defaults to RPA_SCRIPT_INPUT_DIR.",
    )
    parser.add_argument(
        "--debug-root",
        help="Local debug root. When set, output_dir is the script input directory and main.py imports must match that path. Defaults to RPA_DEBUG_ROOT.",
    )
    return parser.parse_args()


def value_from_arg_or_env(arg_value: str | None, env_name: str, label: str) -> str:
    value = arg_value or os.environ.get(env_name)
    if not value:
        fail(f"{label} is required; pass it as an argument or set {env_name}")
    return value


def main() -> int:
    args = parse_args()
    output_dir = Path(value_from_arg_or_env(args.output_dir, "RPA_SCRIPT_INPUT_DIR", "script input directory"))
    debug_root_value = args.debug_root or os.environ.get("RPA_DEBUG_ROOT")
    if not debug_root_value:
        ensure_output_dir(output_dir)
    debug_root = Path(debug_root_value)
    if not output_dir.is_absolute():
        output_dir = debug_root / output_dir
    debug_relative_output = ensure_debug_output_dir(output_dir, debug_root)
    paths = ensure_required_files(output_dir)
    ensure_readme_prompt_contract(paths)
    ensure_no_async(paths)
    ensure_framework_contract(paths)
    ensure_browser_config_contract(paths)
    if debug_relative_output is not None:
        ensure_debug_import_contract(paths, debug_relative_output)
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
