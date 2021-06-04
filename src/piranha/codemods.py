import importlib.util

from libcst import FlattenSentinel, RemoveFromParent, matchers
from libcst.codemod import VisitorBasedCodemodCommand


class PiranhaCommand(VisitorBasedCodemodCommand):
    DESCRIPTION = "Removes feature flag usages from code whilst trying to preserve the implementation's behavior"

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

    def __init__(self, context, flag_name):
        super().__init__(context)
        self.flag_name = flag_name
        self.is_in_feature_flag_block = False
        self.found_return_stmt_in_ff_block = False
        # The function below could be customized in the future by passing its path via codemod arguments
        module_test_function_path = "piranha.codemods._default_test_module_check"
        loaded_test_function_module = importlib.import_module(_parent_of(module_test_function_path))
        self._is_test_module = loaded_test_function_module.__getattribute__(_last_part_of(module_test_function_path))

    def visit_Module(self, node):
        return not self._is_test_module(self.context.full_module_name)

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


def _default_test_module_check(full_module_name):
    if full_module_name is not None:
        filename = _last_part_of(full_module_name)
        return filename.startswith("test_")

    return False


def _parent_of(module_test_function_path):
    return ".".join(module_test_function_path.split(".")[:-1])


def _last_part_of(module_test_function_path):
    return module_test_function_path.split(".")[-1]
