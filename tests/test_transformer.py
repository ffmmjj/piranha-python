import textwrap

from libcst.codemod import CodemodTest
from piranha import PiranhaCommand


class PiranhaCodemodTest(CodemodTest):
    TRANSFORM = PiranhaCommand

    def test_keeps_IF_block_body_having_single_non_return_expression(self):
        feature_flag_name = "FEATURE_FLAG_NAME"
        original_code = _as_clean_str(
            """\
        if %s:
            print('Flag is active')

        print('This is not related to the feature flag value at all')
        """
            % feature_flag_name
        )

        self.assertCodemod(
            original_code,
            _as_clean_str(
                """\
                        print('Flag is active')

                        print('This is not related to the feature flag value at all')
                        """
            ),
            flag_name=feature_flag_name,
        )


def _as_clean_str(expected_code):
    return textwrap.dedent(expected_code).rstrip()
