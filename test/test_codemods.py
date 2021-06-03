import textwrap

from libcst.codemod import CodemodContext, CodemodTest
from piranha.codemods import PiranhaCommand


class PiranhaCodemodTest(CodemodTest):
    TRANSFORM = PiranhaCommand
    FEATURE_FLAG_NAME = "FEATURE_FLAG_NAME"

    def test_keeps_IF_block_body_having_single_non_return_expression(self):
        self.assertCodemod(
            _as_clean_str(
                """\
            if %s:
                print('Flag is active')

            print('This is not related to the feature flag value at all')
            """
                % self.FEATURE_FLAG_NAME
            ),
            _as_clean_str(
                """\
            print('Flag is active')

            print('This is not related to the feature flag value at all')
            """
            ),
            flag_name=self.FEATURE_FLAG_NAME,
        )

    def test_keeps_only_IF_block_body_when_it_has_an_unconditional_return_expression(self):
        self.assertCodemod(
            _as_clean_str(
                """\
            if %s:
                return 0

            print('This is not related to the feature flag value at all')
            """
                % self.FEATURE_FLAG_NAME
            ),
            _as_clean_str(
                """\
            return 0
            """
            ),
            flag_name=self.FEATURE_FLAG_NAME,
        )

    def test_ignores_IF_block_when_processing_a_test_module(self):
        if_block_without_return_stmt = _as_clean_str(
            """\
            if %s:
                print('Flag is active')

            print('This is not related to the feature flag value at all')
            """
            % self.FEATURE_FLAG_NAME
        )
        self.assertCodemod(
            if_block_without_return_stmt,
            if_block_without_return_stmt,
            flag_name=self.FEATURE_FLAG_NAME,
            context_override=_test_module_context(),
        )

        if_block_with_return_stmt = _as_clean_str(
            """\
            if %s:
                return 0

            print('This is not related to the feature flag value at all')
            """
            % self.FEATURE_FLAG_NAME
        )
        self.assertCodemod(
            if_block_with_return_stmt,
            if_block_with_return_stmt,
            flag_name=self.FEATURE_FLAG_NAME,
            context_override=_test_module_context(),
        )


def _test_module_context():
    return CodemodContext(filename="test_module.py")


def _as_clean_str(expected_code):
    return textwrap.dedent(expected_code).rstrip()
