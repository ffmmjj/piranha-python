import textwrap
import unittest

import piranha


class RawBooleanFeatureFlagsTest(unittest.TestCase):
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

        code_with_removed_flag = piranha.remove_flag_from(original_code, feature_flag_name)

        self.assertEqual(
            _as_clean_str(
                """\
                        print('Flag is active')
                        print('This is not related to the feature flag value at all')
                        """
            ),
            code_with_removed_flag,
        )


def _as_clean_str(expected_code):
    return textwrap.dedent(expected_code).rstrip()


if __name__ == "__main__":
    unittest.main()
