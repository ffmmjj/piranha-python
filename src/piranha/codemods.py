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
        return self.flag_name in node.code and not self._ignore_module(self.context.full_module_name)

    def leave_ImportFrom(self, original_node, updated_node):
        imported_names_after_removing_flag = [
            n for n in updated_node.names if not matchers.matches(n.name, matchers.Name(self.flag_name))
        ]
        if len(imported_names_after_removing_flag) == 0:
            return RemoveFromParent()

        return updated_node.with_changes(names=imported_names_after_removing_flag)

    def leave_FunctionDef(self, original_node, updated_node):
        self._reset_traversal_state()

        return updated_node

    def leave_Assign(self, original_node, updated_node):
        if self._is_tuple_assignment(updated_node):
            return self._updated_tuple_assignment(updated_node)

        targets_without_flag = [
            t for t in updated_node.targets if not matchers.matches(t.target, matchers.Name(self.flag_name))
        ]
        if len(targets_without_flag) == 0:
            return RemoveFromParent()

        return updated_node.with_changes(targets=targets_without_flag)

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

    def _updated_tuple_assignment(self, updated_node):
        assignee_tuple = updated_node.targets[0].target
        assignee_tuple_children_without_flag = [
            (i, c)
            for i, c in enumerate(assignee_tuple.children)
            if not matchers.matches(c.value, matchers.Name(self.flag_name))
        ]
        assignee_tuple_children_indices_without_flag = [i for i, _ in assignee_tuple_children_without_flag]
        assigned_tuple = updated_node.value
        return updated_node.with_changes(
            targets=[
                updated_node.targets[0].with_changes(
                    target=assignee_tuple.with_changes(
                        elements=tuple([c for _, c in assignee_tuple_children_without_flag])
                    )
                )
            ],
            value=assigned_tuple.with_changes(
                elements=tuple(
                    [
                        v
                        for i, v in enumerate(assigned_tuple.children)
                        if i in assignee_tuple_children_indices_without_flag
                    ]
                )
            ),
        )

    def _is_tuple_assignment(self, updated_node):
        return len(updated_node.targets) == 1 and matchers.matches(
            updated_node.targets[0].target, matchers.TypeOf(matchers.Tuple)
        )


def _is_test_module(full_module_name):
    if full_module_name is not None:
        filename = _last_part_of(full_module_name)
        return filename.startswith("test_")

    return False


def _parent_of(module_test_function_path):
    return ".".join(module_test_function_path.split(".")[:-1])


def _last_part_of(module_test_function_path):
    return module_test_function_path.split(".")[-1]
