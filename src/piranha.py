"""Main entry point for piranha-python's features."""
import astroid


def remove_flag_from(code_block, flag_to_remove_name):
    """
    Rewrite the code_block assuming that the passed feature flag is True.

    :param code_block: block of python code that will be re-written
    :param flag_to_remove_name: name of the feature flag that should be assumed to be True inside code_block
    :return: a semantics-preserving version of code_block with all references to the passed feature flag removed.
    """
    astroid.MANAGER.register_transform(
        astroid.If, _process_if_block, predicate=lambda node: node.test.name == flag_to_remove_name
    )
    original_ast = astroid.parse(code_block)

    return original_ast.as_string().rstrip()


def _process_if_block(node):
    if_block_body = node.body[0]
    if_block_body.lineno = node.lineno
    if_block_body.col_offset = node.col_offset
    if_block_body.parent = node.parent

    return if_block_body
