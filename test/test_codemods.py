import textwrap

from libcst.codemod import CodemodContext, CodemodTest
from piranha_python.codemods import PiranhaCommand

FEATURE_FLAG_NAME = "FEATURE_FLAG_NAME"


class PiranhaCodemodInitializationTests(CodemodTest):
    TRANSFORM = PiranhaCommand

    def test_lack_of_custom_method_name_raises_exception(self):
        with self.assertRaises(TypeError) as thrown_exception:
            self.assertCodemod(
                "print('This is not related to the feature flag value at all')",
                "print('This is not related to the feature flag value at all')",
                flag_name=FEATURE_FLAG_NAME,
            )

        self.assertIn("flag_resolution_methods", thrown_exception.exception.args[0])


class PiranhaTreatmentFlagTest(CodemodTest):
    TRANSFORM = PiranhaCommand

    def test_keeps_IF_block_body_having_single_non_return_expression(self):
        self.assertCodemod(
            _with_correct_indentation(
                """\
            if is_flag_active(%s):
                print('Flag is active')

            print('This is not related to the feature flag value at all')
            """
                % FEATURE_FLAG_NAME
            ),
            _with_correct_indentation(
                """\
            print('Flag is active')

            print('This is not related to the feature flag value at all')
            """
            ),
            flag_name=FEATURE_FLAG_NAME,
            flag_resolution_methods="is_flag_active",
        )

    def test_treatment_flag_can_be_specified_by_dict_array_instead_of_string(self):
        self.assertCodemod(
            _with_correct_indentation(
                """\
            if is_flag_active(%s):
                print('Flag is active')

            print('This is not related to the feature flag value at all')
            """
                % FEATURE_FLAG_NAME
            ),
            _with_correct_indentation(
                """\
            print('Flag is active')

            print('This is not related to the feature flag value at all')
            """
            ),
            flag_name=FEATURE_FLAG_NAME,
            flag_resolution_methods=[{"methodName": "is_flag_active", "flagType": "treatment"}],
        )

    def test_keeps_only_IF_block_body_when_it_has_an_unconditional_return_expression(self):
        self.assertCodemod(
            _with_correct_indentation(
                """\
            if is_flag_active(%s):
                return 0

            print('This is not related to the feature flag value at all')
            """
                % FEATURE_FLAG_NAME
            ),
            _with_correct_indentation(
                """\
            return 0
            """
            ),
            flag_name=FEATURE_FLAG_NAME,
            flag_resolution_methods="is_flag_active",
        )

    def test_ignores_IF_block_when_processing_a_test_module(self):
        if_block_without_return_stmt = _with_correct_indentation(
            """\
            if is_flag_active(%s):
                print('Flag is active')

            print('This is not related to the feature flag value at all')
            """
            % FEATURE_FLAG_NAME
        )
        self.assertCodemod(
            if_block_without_return_stmt,
            if_block_without_return_stmt,
            flag_name=FEATURE_FLAG_NAME,
            flag_resolution_methods="is_flag_active",
            context_override=_context_representing_test_module(),
        )

        if_block_with_return_stmt = _with_correct_indentation(
            """\
            if is_flag_active(%s):
                return 0

            print('This is not related to the feature flag value at all')
            """
            % FEATURE_FLAG_NAME
        )
        self.assertCodemod(
            if_block_with_return_stmt,
            if_block_with_return_stmt,
            flag_name=FEATURE_FLAG_NAME,
            flag_resolution_methods="is_flag_active",
            context_override=_context_representing_test_module(),
        )

    def test_ignores_IF_block_when_ignored_modules_check_fn_thats_always_true_is_passed(self):
        if_block_without_return_stmt = _with_correct_indentation(
            """\
            if is_flag_active(%s):
                print('Flag is active')

            print('This is not related to the feature flag value at all')
            """
            % FEATURE_FLAG_NAME
        )
        self.assertCodemod(
            if_block_without_return_stmt,
            if_block_without_return_stmt,
            flag_name=FEATURE_FLAG_NAME,
            flag_resolution_methods="is_flag_active",
            ignored_module_check_fn_path="test.test_codemods._always_return_true",
        )

    def test_can_work_with_multiple_defs_in_module(self):
        self.assertCodemod(
            _with_correct_indentation(
                """\
                def func1():
                    if is_flag_active(%(flag_name)s):
                        print('Flag is active')
                        return 0

                    print('This is not related to the feature flag value at all')


                def func2():
                    print('This is not related to the feature flag value at all')

                    if is_flag_active(%(flag_name)s):
                        print('Flag is active')
                """
                % {"flag_name": FEATURE_FLAG_NAME}
            ),
            _with_correct_indentation(
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
            flag_resolution_methods="is_flag_active",
        )

    # Tests covering presence of ELSE blocks
    def test_keeps_ELSE_block_body_when_flag_value_condition_with_custom_method_is_false(self):
        self.assertCodemod(
            _with_correct_indentation(
                """\
            if not is_flag_active(%s):
                print('Flag is active')
            else:
                print('This is not related to the feature flag value at all')

            print('Completely unrelated statement')
            """
                % FEATURE_FLAG_NAME
            ),
            _with_correct_indentation(
                """\
            print('This is not related to the feature flag value at all')

            print('Completely unrelated statement')
            """
            ),
            flag_name=FEATURE_FLAG_NAME,
            flag_resolution_methods="is_flag_active",
        )

    def test_keeps_only_ELSE_block_body_when_it_contains_return_statement_and_flag_value_condition_is_false(self):
        self.assertCodemod(
            _with_correct_indentation(
                """\
            if not is_flag_active(%s):
                print('Flag is active')
            else:
                print('This is not related to the feature flag value at all')
                return 0

            print('Completely unrelated statement')
            """
                % FEATURE_FLAG_NAME
            ),
            _with_correct_indentation(
                """\
            print('This is not related to the feature flag value at all')
            return 0
            """
            ),
            flag_name=FEATURE_FLAG_NAME,
            flag_resolution_methods="is_flag_active",
        )

    def test_keeps_ELSE_block_body_and_remainder_when_IF_block_contains_return_statement_but_ELSE_doesnt(self):
        self.assertCodemod(
            _with_correct_indentation(
                """\
            if not is_flag_active(%s):
                print('Flag is active')
                return 0
            else:
                print('This is not related to the feature flag value at all')

            print('Completely unrelated statement')
            """
                % FEATURE_FLAG_NAME
            ),
            _with_correct_indentation(
                """\
            print('This is not related to the feature flag value at all')

            print('Completely unrelated statement')
            """
            ),
            flag_name=FEATURE_FLAG_NAME,
            flag_resolution_methods="is_flag_active",
        )

    def test_keeps_ELSE_block_body_when_flag_value_condition_is_false(self):
        self.assertCodemod(
            _with_correct_indentation(
                """\
            if not is_flag_active(%s):
                print('Flag is active')
            else:
                print('This is not related to the feature flag value at all')

            print('Completely unrelated statement')
            """
                % FEATURE_FLAG_NAME
            ),
            _with_correct_indentation(
                """\
            print('This is not related to the feature flag value at all')

            print('Completely unrelated statement')
            """
            ),
            flag_name=FEATURE_FLAG_NAME,
            flag_resolution_methods="is_flag_active",
        )

    # Tests covering the presence of docstrings in changed code
    def test_keeps_single_lined_docstring_in_module(self):
        self.assertCodemod(
            _with_correct_indentation(
                """\
            \"\"\" Single lined docstring for this module \"\"\"
            if is_flag_active(%s):
                return 0

            print('This is not related to the feature flag value at all')
            """
                % FEATURE_FLAG_NAME
            ),
            _with_correct_indentation(
                """\
            \"\"\" Single lined docstring for this module \"\"\"
            return 0
            """
            ),
            flag_name=FEATURE_FLAG_NAME,
            flag_resolution_methods="is_flag_active",
        )

    def test_keeps_multi_lined_docstring_in_module(self):
        self.assertCodemod(
            _with_correct_indentation(
                """\
            \"\"\"
            Multi lined
            docstring for this module
            \"\"\"
            if is_flag_active(%s):
                return 0

            print('This is not related to the feature flag value at all')
            """
                % FEATURE_FLAG_NAME
            ),
            _with_correct_indentation(
                """\
            \"\"\"
            Multi lined
            docstring for this module
            \"\"\"
            return 0
            """
            ),
            flag_name=FEATURE_FLAG_NAME,
            flag_resolution_methods="is_flag_active",
        )

    def test_keeps_single_lined_docstring_in_function(self):
        self.assertCodemod(
            _with_correct_indentation(
                """\
            def func1():
                \"\"\" Single lined docstring for this function \"\"\"
                if is_flag_active(%s):
                    return 0

                print('This is not related to the feature flag value at all')
            """
                % FEATURE_FLAG_NAME
            ),
            _with_correct_indentation(
                """\
            def func1():
                \"\"\" Single lined docstring for this function \"\"\"
                return 0
            """
            ),
            flag_name=FEATURE_FLAG_NAME,
            flag_resolution_methods="is_flag_active",
        )

    def test_keeps_multi_lined_docstring_in_function(self):
        self.assertCodemod(
            _with_correct_indentation(
                """\
            def func1():
                \"\"\"
                Multi lined
                docstring for this module
                \"\"\"
                if is_flag_active(%s):
                    return 0

                print('This is not related to the feature flag value at all')
            """
                % FEATURE_FLAG_NAME
            ),
            _with_correct_indentation(
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
            flag_resolution_methods="is_flag_active",
        )

    # Aliased flag names tests
    def test_removes_IF_block_that_uses_aliased_flag_name_via_import_from(self):
        self.assertCodemod(
            _with_correct_indentation(
                """\
            from feature_flags import %(flag_name)s as MY_ALIASED_FLAG_NAME

            if is_flag_active(MY_ALIASED_FLAG_NAME):
                print('Flag is active')

            print('This is not related to the feature flag value at all')
            """
                % {"flag_name": FEATURE_FLAG_NAME}
            ),
            _with_correct_indentation(
                """\
            print('Flag is active')

            print('This is not related to the feature flag value at all')
            """
            ),
            flag_name=FEATURE_FLAG_NAME,
            flag_resolution_methods="is_flag_active",
        )

    def test_removes_IF_block_that_uses_aliased_flag_name_via_simple_import(self):
        self.assertCodemod(
            _with_correct_indentation(
                """\
            import feature_flags.%(flag_name)s as MY_ALIASED_FLAG_NAME

            if is_flag_active(MY_ALIASED_FLAG_NAME):
                print('Flag is active')

            print('This is not related to the feature flag value at all')
            """
                % {"flag_name": FEATURE_FLAG_NAME}
            ),
            _with_correct_indentation(
                """\
            print('Flag is active')

            print('This is not related to the feature flag value at all')
            """
            ),
            flag_name=FEATURE_FLAG_NAME,
            flag_resolution_methods="is_flag_active",
        )


class PiranhaControlFlagTest(CodemodTest):
    TRANSFORM = PiranhaCommand

    def test_keeps_ELSE_block_when_flag_resolution_method_is_set_as_control(self):
        self.assertCodemod(
            _with_correct_indentation(
                """\
            def is_control_resolution_method(f):
                return False


            def not_the_control_resolution_method(f):
                return True


            if is_control_resolution_method(%(flag_name)s):
                print('Flag is active')
            else:
                print('Flag is inactive')

            if not_the_control_resolution_method(%(flag_name)s):
                print('Nothing to see here')
            else:
                print('Nothing to see here either')

            print('This is not related to the feature flag value at all')
            """
                % {"flag_name": FEATURE_FLAG_NAME}
            ),
            _with_correct_indentation(
                """\
            def is_control_resolution_method(f):
                return False


            def not_the_control_resolution_method(f):
                return True
            print('Flag is inactive')

            if not_the_control_resolution_method(%(flag_name)s):
                print('Nothing to see here')
            else:
                print('Nothing to see here either')

            print('This is not related to the feature flag value at all')
            """
                % {"flag_name": FEATURE_FLAG_NAME}
            ),
            flag_name=FEATURE_FLAG_NAME,
            flag_resolution_methods=[{"methodName": "is_control_resolution_method", "flagType": "control"}],
        )

    def test_keeps_IF_block_when_flag_resolution_method_is_set_as_control_and_conditional_is_a_NOT(self):
        self.assertCodemod(
            _with_correct_indentation(
                """\
            def is_control_resolution_method(f):
                return False


            if not is_control_resolution_method(%(flag_name)s):
                print('Flag is inactive')
            else:
                print('Flag is active')

            print('This is not related to the feature flag value at all')
            """
                % {"flag_name": FEATURE_FLAG_NAME}
            ),
            _with_correct_indentation(
                """\
            def is_control_resolution_method(f):
                return False
            print('Flag is inactive')

            print('This is not related to the feature flag value at all')
            """
                % {"flag_name": FEATURE_FLAG_NAME}
            ),
            flag_name=FEATURE_FLAG_NAME,
            flag_resolution_methods=[{"methodName": "is_control_resolution_method", "flagType": "control"}],
        )


class PiranhaCodemodFlagDeclarationRemovalTest(CodemodTest):
    TRANSFORM = PiranhaCommand

    def test_removes_simple_flag_declaration_statement(self):
        self.assertCodemod(
            _with_correct_indentation(
                """\
            %(flag_name)s = True

            if is_flag_active(%(flag_name)s):
                print('Flag is active')

            print('This is not related to the feature flag value at all')
            """
                % {"flag_name": FEATURE_FLAG_NAME}
            ),
            _with_correct_indentation(
                """\
            print('Flag is active')

            print('This is not related to the feature flag value at all')
            """
            ),
            flag_name=FEATURE_FLAG_NAME,
            flag_resolution_methods="is_flag_active",
        )

    def test_removes_only_flag_declaration_from_multiple_assignment_of_same_value_statement(self):
        self.assertCodemod(
            _with_correct_indentation(
                """\
            %(flag_name)s = ANOTHER_FLAG = True

            if is_flag_active(%(flag_name)s):
                print('Flag is active')

            print('This is not related to the feature flag value at all')
            """
                % {"flag_name": FEATURE_FLAG_NAME}
            ),
            _with_correct_indentation(
                """\
            ANOTHER_FLAG = True
            print('Flag is active')

            print('This is not related to the feature flag value at all')
            """
            ),
            flag_name=FEATURE_FLAG_NAME,
            flag_resolution_methods="is_flag_active",
        )

    def test_removes_only_flag_declaration_from_multiple_assignment_via_tuple_unpacking(self):
        self.assertCodemod(
            _with_correct_indentation(
                """\
            ANOTHER_FLAG, %(flag_name)s, YET_ANOTHER_FLAG = False, True, True

            if is_flag_active(%(flag_name)s):
                print('Flag is active')

            print('This is not related to the feature flag value at all')
            """
                % {"flag_name": FEATURE_FLAG_NAME}
            ),
            _with_correct_indentation(
                """\
            ANOTHER_FLAG, YET_ANOTHER_FLAG = False, True
            print('Flag is active')

            print('This is not related to the feature flag value at all')
            """
            ),
            flag_name=FEATURE_FLAG_NAME,
            flag_resolution_methods="is_flag_active",
        )


class PiranhaCodemodFlagImportsHandlingTest(CodemodTest):
    TRANSFORM = PiranhaCommand

    def test_remove_unaliased_flag_from_single_direct_IMPORT_FROM(self):
        self.assertCodemod(
            _with_correct_indentation(
                """\
            from feature_flags import %(flag_name)s


            print('This is not related to the feature flag value at all')
            """
                % {"flag_name": FEATURE_FLAG_NAME}
            ),
            _with_correct_indentation(
                """\
            print('This is not related to the feature flag value at all')
            """
            ),
            flag_name=FEATURE_FLAG_NAME,
            flag_resolution_methods="is_flag_active",
        )

    def test_remove_unaliased_flag_from_multiple_direct_IMPORTS_FROM(self):
        self.assertCodemod(
            _with_correct_indentation(
                """\
            from feature_flags import ANOTHER_FLAG, %(flag_name)s, YET_ANOTHER_FLAG


            print('This is not related to the feature flag value at all')
            """
                % {"flag_name": FEATURE_FLAG_NAME}
            ),
            _with_correct_indentation(
                """\
            from feature_flags import ANOTHER_FLAG, YET_ANOTHER_FLAG


            print('This is not related to the feature flag value at all')
            """
            ),
            flag_name=FEATURE_FLAG_NAME,
            flag_resolution_methods="is_flag_active",
        )

    def test_removes_aliased_flag_along_with_its_IMPORT_FROM_statement(self):
        self.assertCodemod(
            _with_correct_indentation(
                """\
            from feature_flags import %(flag_name)s as MY_ALIASED_FLAG_NAME


            print('This is not related to the feature flag value at all')
            """
                % {"flag_name": FEATURE_FLAG_NAME}
            ),
            _with_correct_indentation(
                """\
            print('This is not related to the feature flag value at all')
            """
            ),
            flag_name=FEATURE_FLAG_NAME,
            flag_resolution_methods="is_flag_active",
        )

    def test_removes_aliased_flag_from_multiple_aliased_IMPORTS_FROM(self):
        self.assertCodemod(
            _with_correct_indentation(
                """\
            from feature_flags import %(flag_name)s as MY_ALIASED_FLAG_NAME, ANOTHER_FLAG as ANOTHER_ALIASED_FLAG


            print('This is not related to the feature flag value at all')
            """
                % {"flag_name": FEATURE_FLAG_NAME}
            ),
            _with_correct_indentation(
                """\
            from feature_flags import ANOTHER_FLAG as ANOTHER_ALIASED_FLAG


            print('This is not related to the feature flag value at all')
            """
            ),
            flag_name=FEATURE_FLAG_NAME,
            flag_resolution_methods="is_flag_active",
        )

    def test_removes_aliased_flag_along_with_its_simple_IMPORT(self):
        self.assertCodemod(
            _with_correct_indentation(
                """\
            import feature_flags.%(flag_name)s as MY_ALIASED_FLAG_NAME

            if is_flag_active(MY_ALIASED_FLAG_NAME):
                print('Flag is active')

            print('This is not related to the feature flag value at all')
            """
                % {"flag_name": FEATURE_FLAG_NAME}
            ),
            _with_correct_indentation(
                """\
            print('Flag is active')

            print('This is not related to the feature flag value at all')
            """
            ),
            flag_name=FEATURE_FLAG_NAME,
            flag_resolution_methods="is_flag_active",
        )

    def test_removes_aliased_flag_along_with_its_simple_IMPORT_but_keeps_other_imports(self):
        self.assertCodemod(
            _with_correct_indentation(
                """\
            import feature_flags.%(flag_name)s as MY_ALIASED_FLAG_NAME, another.symbol as SOMETHING_ELSE


            if is_flag_active(MY_ALIASED_FLAG_NAME):
                print('Flag is active')

            print('This is not related to the feature flag value at all')
            """
                % {"flag_name": FEATURE_FLAG_NAME}
            ),
            _with_correct_indentation(
                """\
            import another.symbol as SOMETHING_ELSE
            print('Flag is active')

            print('This is not related to the feature flag value at all')
            """
            ),
            flag_name=FEATURE_FLAG_NAME,
            flag_resolution_methods="is_flag_active",
        )


class PiranhaCodemodUnchangedCodeTest(CodemodTest):
    TRANSFORM = PiranhaCommand

    def test_doesnt_change_code_if_no_method_matches_the_empty_custom_resolution_method(self):
        self.assertCodemod(
            _with_correct_indentation(
                """\
            def this_is_not_the_flag_method(f):
                return True


            if this_is_not_the_flag_method(%(flag_name)s):
                print('Nothing to see here')
            else:
                print('Nothing to see here either')

            print('This is not related to the feature flag value at all')
            """
                % {"flag_name": FEATURE_FLAG_NAME}
            ),
            _with_correct_indentation(
                """\
            def this_is_not_the_flag_method(f):
                return True


            if this_is_not_the_flag_method(%(flag_name)s):
                print('Nothing to see here')
            else:
                print('Nothing to see here either')

            print('This is not related to the feature flag value at all')
            """
                % {"flag_name": FEATURE_FLAG_NAME}
            ),
            flag_name=FEATURE_FLAG_NAME,
            flag_resolution_methods="is_flag_active",
        )

    def test_doesnt_change_code_if_no_method_matches_the_passed_custom_resolution_method(self):
        self.assertCodemod(
            _with_correct_indentation(
                """\
            def this_is_not_the_flag_method(f):
                return True


            if this_is_not_the_flag_method(%(flag_name)s):
                print('Nothing to see here')
            else:
                print('Nothing to see here either')

            print('This is not related to the feature flag value at all')
            """
                % {"flag_name": FEATURE_FLAG_NAME}
            ),
            _with_correct_indentation(
                """\
            def this_is_not_the_flag_method(f):
                return True


            if this_is_not_the_flag_method(%(flag_name)s):
                print('Nothing to see here')
            else:
                print('Nothing to see here either')

            print('This is not related to the feature flag value at all')
            """
                % {"flag_name": FEATURE_FLAG_NAME}
            ),
            flag_name=FEATURE_FLAG_NAME,
            flag_resolution_methods="is_flag_active",
        )

    def test_doesnt_change_code_when_flag_is_directly_used_as_boolean(self):
        self.assertCodemod(
            _with_correct_indentation(
                """\
            if %(flag_name)s:
                print('Nothing to see here')
            else:
                print('Nothing to see here either')

            print('This is not related to the feature flag value at all')
            """
                % {"flag_name": FEATURE_FLAG_NAME}
            ),
            _with_correct_indentation(
                """\
            if %(flag_name)s:
                print('Nothing to see here')
            else:
                print('Nothing to see here either')

            print('This is not related to the feature flag value at all')
            """
                % {"flag_name": FEATURE_FLAG_NAME}
            ),
            flag_name=FEATURE_FLAG_NAME,
            flag_resolution_methods="is_flag_active",
        )


def _context_representing_test_module():
    return CodemodContext(filename="test_module.py", full_module_name="piranha.test_module")


def _with_correct_indentation(expected_code):
    return textwrap.dedent(expected_code).rstrip()


def _always_return_true(_):
    return True
