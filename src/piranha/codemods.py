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
