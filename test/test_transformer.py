import textwrap

from libcst.codemod import CodemodTest
from piranha import PiranhaCommand


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


def _as_clean_str(expected_code):
    return textwrap.dedent(expected_code).rstrip()
