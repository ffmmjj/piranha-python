import importlib.util

from libcst import FlattenSentinel, RemoveFromParent, matchers
from libcst.codemod import VisitorBasedCodemodCommand


class PiranhaCommand(VisitorBasedCodemodCommand):
    DESCRIPTION = "Removes feature flag usages from code whilst trying to preserve the implementation's behavior"
    DEFAULT_TEST_MODULE_CHECK_PATH = "piranha.codemods._is_test_module"

    @staticmethod
    def add_args(arg_parser):
        arg_parser.add_argument(
            "--flag-name",
            dest="flag_name",
            metavar="FLAG_NAME",
            help="Name of the feature flag to be processed",
            type=str,
            required=True,
        )
        arg_parser.add_argument(
            "--ignored-module-check-path",
            dest="ignored_module_check_fn_path",
            metavar="IGNORED_MODULE_CHECK_FN_PATH",
            help="Path to a function that says whether a given module should be ignored given its full dotted path",
            type=str,
            required=False,
        )

    def __init__(self, context, flag_name, ignored_module_check_fn_path=None):
        super().__init__(context)
        self.flag_name = flag_name
        self._reset_traversal_state()

        if ignored_module_check_fn_path is None:
            ignored_module_check_fn_path = self.DEFAULT_TEST_MODULE_CHECK_PATH

        loaded_ignore_function_module = importlib.import_module(_parent_of(ignored_module_check_fn_path))
        self._ignore_module = loaded_ignore_function_module.__getattribute__(
            _last_part_of(ignored_module_check_fn_path)
        )

    def visit_Module(self, node):
        return not self._ignore_module(self.context.full_module_name)

    def leave_FunctionDef(self, original_node, updated_node):
        self._reset_traversal_state()

        return updated_node

    def leave_Assign(self, original_node, updated_node):
        if any(matchers.matches(t.target, matchers.Name(self.flag_name)) for t in updated_node.targets):
            return RemoveFromParent()

        return updated_node

    def visit_If(self, node):
        self.is_in_feature_flag_block = matchers.matches(node.test, matchers.Name(self.flag_name))
        return True

    def leave_If(self, original_node, updated_node):
        if self.is_in_feature_flag_block:
            return_statements = matchers.findall(original_node.body, matchers.Return())
            self.found_return_stmt_in_ff_block = len(return_statements) > 0

            self.is_in_feature_flag_block = False
            return FlattenSentinel(original_node.body.body)

    def leave_SimpleStatementLine(self, original_node, updated_node):
        if not self.is_in_feature_flag_block and self.found_return_stmt_in_ff_block:
            return RemoveFromParent()

        return updated_node

    def _reset_traversal_state(self):
        self.is_in_feature_flag_block = False
        self.found_return_stmt_in_ff_block = False


def _is_test_module(full_module_name):
    if full_module_name is not None:
        filename = _last_part_of(full_module_name)
        return filename.startswith("test_")

    return False


def _parent_of(module_test_function_path):
    return ".".join(module_test_function_path.split(".")[:-1])


def _last_part_of(module_test_function_path):
    return module_test_function_path.split(".")[-1]
