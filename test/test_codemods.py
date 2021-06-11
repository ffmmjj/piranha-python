import textwrap

from libcst.codemod import CodemodContext, CodemodTest
from piranha.codemods import PiranhaCommand

FEATURE_FLAG_NAME = "FEATURE_FLAG_NAME"


class PiranhaBranchesFlowWithoutExplicitElseTest(CodemodTest):
    TRANSFORM = PiranhaCommand

    def test_keeps_IF_block_body_having_single_non_return_expression(self):
        self.assertCodemod(
            _as_clean_str(
                """\
            if %s:
                print('Flag is active')

            print('This is not related to the feature flag value at all')
            """
                % FEATURE_FLAG_NAME
            ),
            _as_clean_str(
                """\
            print('Flag is active')

            print('This is not related to the feature flag value at all')
            """
            ),
            flag_name=FEATURE_FLAG_NAME,
        )

    def test_keeps_only_IF_block_body_when_it_has_an_unconditional_return_expression(self):
        self.assertCodemod(
            _as_clean_str(
                """\
            if %s:
                return 0

            print('This is not related to the feature flag value at all')
            """
                % FEATURE_FLAG_NAME
            ),
            _as_clean_str(
                """\
            return 0
            """
            ),
            flag_name=FEATURE_FLAG_NAME,
        )

    def test_ignores_IF_block_when_processing_a_test_module(self):
        if_block_without_return_stmt = _as_clean_str(
            """\
            if %s:
                print('Flag is active')

            print('This is not related to the feature flag value at all')
            """
            % FEATURE_FLAG_NAME
        )
        self.assertCodemod(
            if_block_without_return_stmt,
            if_block_without_return_stmt,
            flag_name=FEATURE_FLAG_NAME,
            context_override=_test_module_context(),
        )

        if_block_with_return_stmt = _as_clean_str(
            """\
            if %s:
                return 0

            print('This is not related to the feature flag value at all')
            """
            % FEATURE_FLAG_NAME
        )
        self.assertCodemod(
            if_block_with_return_stmt,
            if_block_with_return_stmt,
            flag_name=FEATURE_FLAG_NAME,
            context_override=_test_module_context(),
        )

    def test_ignores_IF_block_when_ignored_modules_check_fn_thats_always_true_is_passed(self):
        if_block_without_return_stmt = _as_clean_str(
            """\
            if %s:
                print('Flag is active')

            print('This is not related to the feature flag value at all')
            """
            % FEATURE_FLAG_NAME
        )
        self.assertCodemod(
            if_block_without_return_stmt,
            if_block_without_return_stmt,
            flag_name=FEATURE_FLAG_NAME,
            ignored_module_check_fn_path="test.test_codemods._always_return_true",
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
                % {"flag_name": FEATURE_FLAG_NAME}
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
                % {"flag_name": FEATURE_FLAG_NAME}
            ),
            flag_name=FEATURE_FLAG_NAME,
        )


class PiranhaBranchesFlowWithExplicitElseTest(CodemodTest):
    TRANSFORM = PiranhaCommand

    def test_keeps_ELSE_block_body_when_flag_value_condition_is_false(self):
        self.assertCodemod(
            _as_clean_str(
                """\
            if not %s:
                print('Flag is active')
            else:
                print('This is not related to the feature flag value at all')

            print('Completely unrelated statement')
            """
                % FEATURE_FLAG_NAME
            ),
            _as_clean_str(
                """\
            print('This is not related to the feature flag value at all')

            print('Completely unrelated statement')
            """
            ),
            flag_name=FEATURE_FLAG_NAME,
        )

    def test_keeps_ELSE_block_body_when_flag_value_condition_with_custom_method_is_false(self):
        self.assertCodemod(
            _as_clean_str(
                """\
            if not is_flag_active(%s):
                print('Flag is active')
            else:
                print('This is not related to the feature flag value at all')

            print('Completely unrelated statement')
            """
                % FEATURE_FLAG_NAME
            ),
            _as_clean_str(
                """\
            print('This is not related to the feature flag value at all')

            print('Completely unrelated statement')
            """
            ),
            flag_name=FEATURE_FLAG_NAME,
            method_name="is_flag_active",
        )


class PiranhaCodemodDocstringsTest(CodemodTest):
    TRANSFORM = PiranhaCommand

    def test_keeps_single_lined_docstring_in_module(self):
        self.assertCodemod(
            _as_clean_str(
                """\
            \"\"\" Single lined docstring for this module \"\"\"
            if %s:
                return 0

            print('This is not related to the feature flag value at all')
            """
                % FEATURE_FLAG_NAME
            ),
            _as_clean_str(
                """\
            \"\"\" Single lined docstring for this module \"\"\"
            return 0
            """
            ),
            flag_name=FEATURE_FLAG_NAME,
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
                % FEATURE_FLAG_NAME
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
            flag_name=FEATURE_FLAG_NAME,
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
                % FEATURE_FLAG_NAME
            ),
            _as_clean_str(
                """\
            def func1():
                \"\"\" Single lined docstring for this function \"\"\"
                return 0
            """
            ),
            flag_name=FEATURE_FLAG_NAME,
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
                % FEATURE_FLAG_NAME
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
            flag_name=FEATURE_FLAG_NAME,
        )


class PiranhaCodemodFlagDeclarationRemovalTest(CodemodTest):
    TRANSFORM = PiranhaCommand

    def test_removes_simple_flag_declaration_statement(self):
        self.assertCodemod(
            _as_clean_str(
                """\
            %(flag_name)s = True

            if %(flag_name)s:
                print('Flag is active')

            print('This is not related to the feature flag value at all')
            """
                % {"flag_name": FEATURE_FLAG_NAME}
            ),
            _as_clean_str(
                """\
            print('Flag is active')

            print('This is not related to the feature flag value at all')
            """
            ),
            flag_name=FEATURE_FLAG_NAME,
        )

    def test_removes_only_flag_declaration_from_multiple_assignment_of_same_value_statement(self):
        self.assertCodemod(
            _as_clean_str(
                """\
            %(flag_name)s = ANOTHER_FLAG = True

            if %(flag_name)s:
                print('Flag is active')

            print('This is not related to the feature flag value at all')
            """
                % {"flag_name": FEATURE_FLAG_NAME}
            ),
            _as_clean_str(
                """\
            ANOTHER_FLAG = True
            print('Flag is active')

            print('This is not related to the feature flag value at all')
            """
            ),
            flag_name=FEATURE_FLAG_NAME,
        )

    def test_removes_only_flag_declaration_from_multiple_assignment_via_tuple_unpacking(self):
        self.assertCodemod(
            _as_clean_str(
                """\
            ANOTHER_FLAG, %(flag_name)s, YET_ANOTHER_FLAG = False, True, True

            if %(flag_name)s:
                print('Flag is active')

            print('This is not related to the feature flag value at all')
            """
                % {"flag_name": FEATURE_FLAG_NAME}
            ),
            _as_clean_str(
                """\
            ANOTHER_FLAG, YET_ANOTHER_FLAG = False, True
            print('Flag is active')

            print('This is not related to the feature flag value at all')
            """
            ),
            flag_name=FEATURE_FLAG_NAME,
        )


class PiranhaCodemodFlagImportsHandlingTest(CodemodTest):
    TRANSFORM = PiranhaCommand

    def test_remove_unaliased_flag_from_single_direct_import(self):
        self.assertCodemod(
            _as_clean_str(
                """\
            from feature_flags import %(flag_name)s


            print('This is not related to the feature flag value at all')
            """
                % {"flag_name": FEATURE_FLAG_NAME}
            ),
            _as_clean_str(
                """\
            print('This is not related to the feature flag value at all')
            """
            ),
            flag_name=FEATURE_FLAG_NAME,
        )

    def test_remove_unaliased_flag_from_multiple_direct_imports(self):
        self.assertCodemod(
            _as_clean_str(
                """\
            from feature_flags import ANOTHER_FLAG, %(flag_name)s, YET_ANOTHER_FLAG


            print('This is not related to the feature flag value at all')
            """
                % {"flag_name": FEATURE_FLAG_NAME}
            ),
            _as_clean_str(
                """\
            from feature_flags import ANOTHER_FLAG, YET_ANOTHER_FLAG


            print('This is not related to the feature flag value at all')
            """
            ),
            flag_name=FEATURE_FLAG_NAME,
        )

    def test_removes_aliased_flag_along_with_its_import_statement(self):
        self.assertCodemod(
            _as_clean_str(
                """\
            from feature_flags import %(flag_name)s as MY_ALIASED_FLAG_NAME


            print('This is not related to the feature flag value at all')
            """
                % {"flag_name": FEATURE_FLAG_NAME}
            ),
            _as_clean_str(
                """\
            print('This is not related to the feature flag value at all')
            """
            ),
            flag_name=FEATURE_FLAG_NAME,
        )

    def test_removes_aliased_flag_from_multiple_aliased_imports(self):
        self.assertCodemod(
            _as_clean_str(
                """\
            from feature_flags import %(flag_name)s as MY_ALIASED_FLAG_NAME, ANOTHER_FLAG as ANOTHER_ALIASED_FLAG


            print('This is not related to the feature flag value at all')
            """
                % {"flag_name": FEATURE_FLAG_NAME}
            ),
            _as_clean_str(
                """\
            from feature_flags import ANOTHER_FLAG as ANOTHER_ALIASED_FLAG


            print('This is not related to the feature flag value at all')
            """
            ),
            flag_name=FEATURE_FLAG_NAME,
        )


class PiranhaCustomFlagResolutionTest(CodemodTest):
    TRANSFORM = PiranhaCommand

    def test_can_resolve_flag_via_custom_method_name(self):
        self.assertCodemod(
            _as_clean_str(
                """\
            def is_flag_active(f):
                return True


            def this_is_not_the_flag_method(f):
                return True


            if is_flag_active(%(flag_name)s):
                print('Flag is active')

            if this_is_not_the_flag_method(%(flag_name)s):
                print('Nothing to see here')

            print('This is not related to the feature flag value at all')
            """
                % {"flag_name": FEATURE_FLAG_NAME}
            ),
            _as_clean_str(
                """\
            def is_flag_active(f):
                return True


            def this_is_not_the_flag_method(f):
                return True
            print('Flag is active')

            if this_is_not_the_flag_method(%(flag_name)s):
                print('Nothing to see here')

            print('This is not related to the feature flag value at all')
            """
                % {"flag_name": FEATURE_FLAG_NAME}
            ),
            flag_name=FEATURE_FLAG_NAME,
            method_name="is_flag_active",
        )


def _test_module_context():
    return CodemodContext(filename="test_module.py", full_module_name="piranha.test_module")


def _as_clean_str(expected_code):
    return textwrap.dedent(expected_code).rstrip()


def _always_return_true(_):
    return True
