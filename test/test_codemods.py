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

    def test_ignores_IF_block_when_ignored_modules_check_fn_thats_always_true_is_passed(self):
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
            ignored_module_check_fn_path="test.test_codemods._always_return_true",
        )

    def test_keeps_single_lined_docstring_in_module(self):
        self.assertCodemod(
            _as_clean_str(
                """\
            \"\"\" Single lined docstring for this module \"\"\"
            if %s:
                return 0

            print('This is not related to the feature flag value at all')
            """
                % self.FEATURE_FLAG_NAME
            ),
            _as_clean_str(
                """\
            \"\"\" Single lined docstring for this module \"\"\"
            return 0
            """
            ),
            flag_name=self.FEATURE_FLAG_NAME,
        )

    def test_keeps_multi_lined_docstring_in_module(self):
        self.assertCodemod(
            _as_clean_str(
                """\
            \"\"\"
            Multi lined
            docstring for this module
            \"\"\"
            if %s:
                return 0

            print('This is not related to the feature flag value at all')
            """
                % self.FEATURE_FLAG_NAME
            ),
            _as_clean_str(
                """\
            \"\"\"
            Multi lined
            docstring for this module
            \"\"\"
            return 0
            """
            ),
            flag_name=self.FEATURE_FLAG_NAME,
        )

    def test_keeps_single_lined_docstring_in_function(self):
        self.assertCodemod(
            _as_clean_str(
                """\
            def func1():
                \"\"\" Single lined docstring for this function \"\"\"
                if %s:
                    return 0

                print('This is not related to the feature flag value at all')
            """
                % self.FEATURE_FLAG_NAME
            ),
            _as_clean_str(
                """\
            def func1():
                \"\"\" Single lined docstring for this function \"\"\"
                return 0
            """
            ),
            flag_name=self.FEATURE_FLAG_NAME,
        )

    def test_keeps_multi_lined_docstring_in_function(self):
        self.assertCodemod(
            _as_clean_str(
                """\
            def func1():
                \"\"\"
                Multi lined
                docstring for this module
                \"\"\"
                if %s:
                    return 0

                print('This is not related to the feature flag value at all')
            """
                % self.FEATURE_FLAG_NAME
            ),
            _as_clean_str(
                """\
            def func1():
                \"\"\"
                Multi lined
                docstring for this module
                \"\"\"
                return 0
            """
            ),
            flag_name=self.FEATURE_FLAG_NAME,
        )

    def test_can_work_with_multiple_defs_in_module(self):
        self.assertCodemod(
            _as_clean_str(
                """\
                def func1():
                    if %(flag_name)s:
                        print('Flag is active')
                        return 0

                    print('This is not related to the feature flag value at all')


                def func2():
                    print('This is not related to the feature flag value at all')

                    if %(flag_name)s:
                        print('Flag is active')
                """
                % {"flag_name": self.FEATURE_FLAG_NAME}
            ),
            _as_clean_str(
                """\
                def func1():
                    print('Flag is active')
                    return 0


                def func2():
                    print('This is not related to the feature flag value at all')
                    print('Flag is active')
                """
                % {"flag_name": self.FEATURE_FLAG_NAME}
            ),
            flag_name=self.FEATURE_FLAG_NAME,
        )


def _test_module_context():
    return CodemodContext(filename="test_module.py", full_module_name="piranha.test_module")


def _as_clean_str(expected_code):
    return textwrap.dedent(expected_code).rstrip()


def _always_return_true(_):
    return True
