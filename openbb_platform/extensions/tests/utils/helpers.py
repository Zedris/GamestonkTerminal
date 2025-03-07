"""Test helpers."""

import ast
import doctest
import glob
import importlib
import inspect
import logging
import os
import re
from importlib.metadata import entry_points
from inspect import getmembers, isfunction
from typing import Any, Dict, List, Set, Tuple

from openbb_core.app.provider_interface import ProviderInterface

pi = ProviderInterface()

logging.basicConfig(level=logging.INFO)


def get_packages_info() -> Dict[str, str]:
    """Get the paths and names of all the static packages."""
    paths_and_names: Dict[str, str] = {}
    package_paths = glob.glob("openbb_platform/openbb/package/*.py")
    for path in package_paths:
        name = os.path.basename(path).split(".")[0]
        paths_and_names[path] = name

    paths_and_names = {
        path: name for path, name in paths_and_names.items() if not name.startswith("_")
    }
    return paths_and_names


def execute_docstring_examples(module_name: str, path: str) -> List[str]:
    """Execute the docstring examples of a module."""
    errors = []
    module = importlib.import_module(f"openbb.package.{module_name}")
    doc_tests = doctest.DocTestFinder().find(module)

    for dt in doc_tests:
        code = "".join([ex.source for ex in dt.examples])
        try:
            exec(code)  # pylint: disable=exec-used  # noqa: S102
        except Exception as e:
            errors.append(
                f"\n\n{'_'*136}\nPath: {path}\nCode:\n{code}\nError: {str(e)}"
            )

    return errors


def check_docstring_examples() -> List[str]:
    """Test that the docstring examples execute without errors."""
    errors = []
    paths_and_names = get_packages_info()

    for path, name in paths_and_names.items():
        result = execute_docstring_examples(name, path)
        if result:
            errors.extend(result)

    return errors


def list_openbb_extensions() -> Tuple[Set[str], Set[str], Set[str]]:
    """List installed openbb extensions and providers.

    Returns
    -------
    Tuple[Set[str], Set[str]]
        First element: set of installed core extensions.
        Second element: set of installed provider extensions.
        Third element: set of installed obbject extensions.
    """

    core_extensions = set()
    provider_extensions = set()
    obbject_extensions = set()
    entry_points_dict = entry_points()

    for entry_point in entry_points_dict.get("openbb_core_extension", []):
        core_extensions.add(f"{entry_point.name}")

    for entry_point in entry_points_dict.get("openbb_provider_extension", []):
        provider_extensions.add(f"{entry_point.name}")

    for entry_point in entry_points_dict.get("openbb_obbject_extension", []):
        obbject_extensions.add(f"{entry_point.name}")

    return core_extensions, provider_extensions, obbject_extensions


def collect_routers(target_dir: str) -> List[str]:
    """Collect all routers in the target directory."""
    current_dir = os.path.dirname(__file__)
    base_path = os.path.abspath(os.path.join(current_dir, "../../../"))

    full_target_path = os.path.abspath(os.path.join(base_path, target_dir))
    routers = []

    for root, _, files in os.walk(full_target_path):
        for name in files:
            if name.endswith("_router.py"):
                full_path = os.path.join(root, name)
                # Convert the full path to a module path
                relative_path = os.path.relpath(full_path, base_path)
                module_path = relative_path.replace("/", ".").replace(".py", "")
                routers.append(module_path)

    return routers


def import_routers(routers: List) -> List:
    """Import all routers."""
    loaded_routers: List = []
    for router in routers:
        module = importlib.import_module(router)
        loaded_routers.append(module)

    return loaded_routers


def collect_router_functions(loaded_routers: List) -> Dict:
    """Collect all router functions."""
    router_functions = {}
    for router in loaded_routers:
        router_functions[router.__name__] = [
            function[1]
            for function in getmembers(router, isfunction)
            if function[0] != "router"
        ]

    return router_functions


def find_decorator(file_path: str, function_name: str) -> str:
    """Find the @router.command decorator of the function in the file, supporting multiline decorators."""
    this_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(
        this_dir.split("openbb_platform/")[0], "openbb_platform", file_path
    )

    with open(file_path) as file:
        lines = file.readlines()

    decorator_lines = []
    capturing_decorator = False
    for line in lines:
        stripped_line = line.strip()
        # Start capturing lines if we encounter a decorator
        if stripped_line.startswith("@router.command"):
            capturing_decorator = True
            decorator_lines.append(stripped_line)
        elif capturing_decorator:
            # If we're currently capturing a decorator and the line is part of it (indentation or open parenthesis)
            if (
                stripped_line.startswith("@")
                or "def" in stripped_line
                and function_name in stripped_line
            ):
                # If we've reached another decorator or the function definition, stop capturing
                capturing_decorator = False
                # If it's the target function, break, else clear decorator_lines for the next decorator
                if "def" in stripped_line and function_name in stripped_line:
                    break
                decorator_lines = []
            else:
                # It's part of the multiline decorator
                decorator_lines.append(stripped_line)

    decorator = " ".join(decorator_lines)
    return decorator


def get_decorator_details(function):
    """Extract decorators and their arguments from a function as dictionaries."""
    source = inspect.getsource(function)
    parsed_source = ast.parse(source)

    if isinstance(parsed_source.body[0], (ast.FunctionDef, ast.AsyncFunctionDef)):
        func_def = parsed_source.body[0]
        for decorator in func_def.decorator_list:
            decorator_detail = {"decorator": "", "args": {}, "keywords": {}}
            if isinstance(decorator, ast.Call):
                decorator_detail["decorator"] = (
                    decorator.func.id
                    if isinstance(decorator.func, ast.Name)
                    else ast.unparse(decorator.func)
                )
                decorator_detail["args"] = {
                    i: ast.unparse(arg) for i, arg in enumerate(decorator.args)
                }
                decorator_detail["keywords"] = {
                    kw.arg: ast.unparse(kw.value) for kw in decorator.keywords
                }
            else:
                decorator_detail["decorator"] = (
                    decorator.id
                    if isinstance(decorator, ast.Name)
                    else ast.unparse(decorator)
                )

    return decorator_detail


def find_missing_router_function_models(
    router_functions: Dict, pi_map: Dict
) -> List[str]:
    """Find the missing models in the router functions."""
    missing_models: List[str] = []
    for router_name, functions in router_functions.items():
        for function in functions:
            decorator = find_decorator(
                os.path.join(*router_name.split(".")) + ".py",
                function.__name__,
            )
            if (
                decorator
                and "model" in decorator
                and "POST" not in decorator
                and "GET" not in decorator
            ):
                model = decorator.split("model=")[1].split(",")[0].strip('"')
                if (
                    model not in pi_map
                    and "POST" not in decorator
                    and "GET" not in decorator
                ):
                    missing_models.append(
                        f"{function.__name__} in {router_name} model doesn't exist in the provider interface map."
                    )

    return missing_models


def parse_example_string(example_string: str) -> Dict[str, Any]:
    """Parses a string of examples into nested dictionaries.

    This is capturing all instances of PythonEx and APIEx, including their "parameters", "code", and "description".
    """
    # Initialize the result dictionary
    result = {}

    # Regular expression patterns to find PythonEx and APIEx examples
    pythonex_pattern = r"PythonEx\(.*?code=(\[.*?\]).*?\)"
    apiex_pattern = r"APIEx\(.*?parameters=(\{.*?\}).*?\)"

    # Function to parse individual examples
    def parse_examples(matches, example_type):
        examples = []
        for match in matches:
            examples.append(
                {"code": [match]} if example_type == "PythonEx" else {"params": match}
            )
        return examples

    # Find and parse all PythonEx examples
    pythonex_matches = re.findall(pythonex_pattern, example_string, re.DOTALL)
    result["PythonEx"] = parse_examples(pythonex_matches, "PythonEx")

    # Find and parse all APIEx examples
    apiex_matches = re.findall(apiex_pattern, example_string, re.DOTALL)
    result["APIEx"] = parse_examples(apiex_matches, "APIEx")

    return result


def get_required_fields(model: str) -> List[str]:
    """Get the required fields of a model."""
    fields = pi.map[model]["openbb"]["QueryParams"]["fields"]
    return [field for field, info in fields.items() if info.is_required()]
