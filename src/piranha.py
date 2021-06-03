from libcst import FlattenSentinel, matchers
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

    def leave_If(self, original_node, updated_node):
        if matchers.matches(original_node.test, matchers.Name(self.flag_name)):
            return FlattenSentinel(original_node.body.body)
