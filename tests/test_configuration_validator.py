"""This module contains tests for pydantic validator configurations.

"""

from docutils.nodes import (
    paragraph,
    emphasis,
)
from sphinx.addnodes import (
    desc,
    desc_signature,
    desc_name,
    desc_content,
    desc_annotation,
    desc_addname,
    pending_xref,
    index
)
from sphinx.testing.util import assert_node
from sphinxcontrib.autodoc_pydantic import PydanticValidatorDocumenter

KWARGS = dict(documenter=PydanticValidatorDocumenter.objtype,
              deactivate_all=True)


def test_autodoc_pydantic_validator_replace_signature_true(autodocument):
    kwargs = dict(
        object_path='target.configuration.ValidatorReplaceSignature.check',
        **KWARGS)
    
    result = [
        '',
        '.. py:pydantic_validator:: ValidatorReplaceSignature.check',
        '   :module: target.configuration',
        '   :classmethod:',
        '',
        '   Check.',
        ''
    ]

    # explict global
    actual = autodocument(
        options_app={"autodoc_pydantic_validator_replace_signature": True},
        **kwargs)
    assert result == actual

    # explict local
    result = [
        '',
        '.. py:pydantic_validator:: ValidatorReplaceSignature.check',
        '   :module: target.configuration',
        '   :classmethod:',
        '   :validator-replace-signature: True',
        '',
        '   Check.',
        ''
    ]

    actual = autodocument(
        options_doc={"validator-replace-signature": True},
        **kwargs)
    assert result == actual

    # explicit local overwrite global
    result = [
        '',
        '.. py:pydantic_validator:: ValidatorReplaceSignature.check',
        '   :module: target.configuration',
        '   :classmethod:',
        '   :validator-replace-signature: True',
        '',
        '   Check.',
        ''
    ]

    actual = autodocument(
        options_app={"autodoc_pydantic_validator_replace_signature": False},
        options_doc={"validator-replace-signature": True},
        **kwargs)
    assert result == actual


def test_autodoc_pydantic_validator_replace_signature_false(autodocument):
    kwargs = dict(
        object_path='target.configuration.ValidatorReplaceSignature.check',
        **KWARGS)

    # explict global
    result = [
        '',
        '.. py:pydantic_validator:: ValidatorReplaceSignature.check(v) -> str',
        '   :module: target.configuration',
        '   :classmethod:',
        '',
        '   Check.',
        ''
    ]

    actual = autodocument(
        options_app={"autodoc_pydantic_validator_replace_signature": False},
        **kwargs)
    assert result == actual

    # explict local
    result = [
        '',
        '.. py:pydantic_validator:: ValidatorReplaceSignature.check(v) -> str',
        '   :module: target.configuration',
        '   :classmethod:',
        '   :validator-replace-signature: False',
        '',
        '   Check.',
        ''
    ]

    actual = autodocument(
        options_doc={"validator-replace-signature": False},
        **kwargs)
    assert result == actual

    # explicit local overwrite global
    actual = autodocument(
        options_app={"autodoc_pydantic_validator_replace_signature": True},
        options_doc={"validator-replace-signature": False},
        **kwargs)
    assert result == actual


def test_autodoc_pydantic_validator_replace_signature_true_directive(
        parse_rst):
    """Tests pydantic_validator directive.

    """

    output_nodes = (
        index,
        [desc, ([desc_signature, ([desc_annotation, "validator "],
                                  [desc_addname, "ValidatorReplaceSignature."],
                                  [desc_name, "check"],
                                  [desc_annotation, "  »  "],
                                  [pending_xref, ([emphasis, "field"])])],
                [desc_content, ([paragraph, "Check."])])
         ]
    )

    # explicit local
    input_rst = [
        '',
        '.. py:pydantic_validator:: ValidatorReplaceSignature.check',
        '   :module: target.configuration',
        '   :classmethod:',
        '   :validator-replace-signature: True',
        '',
        '   Check.',
        ''
    ]
    doctree = parse_rst(input_rst)
    assert_node(doctree, output_nodes)

    # explicit global
    input_rst = [
        '',
        '.. py:pydantic_validator:: ValidatorReplaceSignature.check',
        '   :module: target.configuration',
        '   :classmethod:',
        '',
        '   Check.',
        ''
    ]
    doctree = parse_rst(input_rst,
                        conf={
                            "autodoc_pydantic_validator_replace_signature": True})
    assert_node(doctree, output_nodes)


def test_autodoc_pydantic_validator_list_fields_true(autodocument):
    kwargs = dict(
        object_path='target.configuration.ValidatorListFields.check',
        **KWARGS)

    result = [
        '',
        '.. py:pydantic_validator:: ValidatorListFields.check',
        '   :module: target.configuration',
        '   :classmethod:',
        '',
        '   Check.',
        '',
        '   :Validates:',
        '      - :py:obj:`field <target.configuration.ValidatorListFields.field>`',
        ''
    ]

    # explict global
    actual = autodocument(
        options_app={"autodoc_pydantic_validator_list_fields": True},
        **kwargs)
    assert result == actual

    # explict local
    actual = autodocument(
        options_doc={"validator-list-fields": True},
        **kwargs)
    assert result == actual

    # explict global
    actual = autodocument(
        options_app={"autodoc_pydantic_validator_list_fields": False},
        options_doc={"validator-list-fields": True},
        **kwargs)
    assert result == actual


def test_autodoc_pydantic_validator_list_fields_false(autodocument):
    kwargs = dict(
        object_path='target.configuration.ValidatorListFields.check',
        **KWARGS)

    result = [
        '',
        '.. py:pydantic_validator:: ValidatorListFields.check',
        '   :module: target.configuration',
        '   :classmethod:',
        '',
        '   Check.',
        ''
    ]

    # explict global
    actual = autodocument(
        options_app={"autodoc_pydantic_validator_list_fields": False},
        **kwargs)
    assert result == actual

    # explict local
    actual = autodocument(
        options_doc={"validator-list-fields": False},
        **kwargs)
    assert result == actual

    # explict global
    actual = autodocument(
        options_app={"autodoc_pydantic_validator_list_fields": True},
        options_doc={"validator-list-fields": False},
        **kwargs)
    assert result == actual


def test_autodoc_pydantic_validator_signature_prefix(autodocument):
    kwargs = dict(
        object_path='target.configuration.ValidatorSignaturePrefix.check',
        **KWARGS)

    # default
    result = [
        '',
        ".. py:pydantic_validator:: ValidatorSignaturePrefix.check",
        '   :module: target.configuration',
        '   :classmethod:',
        '',
        '   Check.',
        ''
    ]

    actual = autodocument(**kwargs)
    assert result == actual

    # explicit value
    result = [
        '',
        ".. py:pydantic_validator:: ValidatorSignaturePrefix.check",
        '   :module: target.configuration',
        '   :classmethod:',
        '   :validator-signature-prefix: foobar',
        '',
        '   Check.',
        ''
    ]

    actual = autodocument(
        options_doc={"validator-signature-prefix": "foobar"},
        **kwargs)
    assert result == actual

    # explict empty
    result = [
        '',
        ".. py:pydantic_validator:: ValidatorSignaturePrefix.check",
        '   :module: target.configuration',
        '   :classmethod:',
        '   :validator-signature-prefix: ',
        '',
        '   Check.',
        ''
    ]

    actual = autodocument(
        options_doc={"validator-signature-prefix": ""},
        **kwargs)
    assert result == actual


def test_autodoc_pydantic_validator_signature_prefix_directive(parse_rst):
    # default
    input_rst = [
        '',
        ".. py:pydantic_validator:: ValidatorSignaturePrefix.check",
        '   :module: target.configuration',
        '   :classmethod:',
        '',
        '   Check.',
        ''
    ]

    doctree = parse_rst(input_rst)
    assert_node(doctree[1][0][0], [desc_annotation, "validator "])

    # empty
    doctree = parse_rst(input_rst,
                        conf={
                            "autodoc_pydantic_validator_signature_prefix": ""})
    assert_node(doctree[1][0][0], [desc_annotation, "classmethod "])

    # custom
    input_rst = [
        '',
        ".. py:pydantic_validator:: ValidatorSignaturePrefix.check",
        '   :module: target.configuration',
        '   :classmethod:',
        '   :validator-signature-prefix: foobar',
        '',
        '   Check.',
        ''
    ]

    doctree = parse_rst(input_rst)
    assert_node(doctree[1][0][0], [desc_annotation, "foobar "])


def test_autodoc_pydantic_validator_asterisk(parse_rst):
    """Tests correct modification for asterisk validator adding " » all fields".

    """

    output_nodes = (
        index,
        [desc, ([desc_signature, ([desc_annotation, "validator "],
                                  [desc_addname,
                                   "ValidatorAsteriskRootValidator."],
                                  [desc_name, "check"],
                                  [desc_annotation, "  »  "],
                                  [pending_xref, ([emphasis, "all fields"])])],
                [desc_content])
         ]
    )

    # explicit local
    input_rst = [
        '',
        '.. py:pydantic_validator:: ValidatorAsteriskRootValidator.check',
        '   :module: target.configuration',
        '   :classmethod:',
        '   :validator-replace-signature: True',
        ''
    ]
    doctree = parse_rst(input_rst)
    assert_node(doctree, output_nodes)


def test_autodoc_pydantic_validator_root(parse_rst):
    """Tests correct modification for root validator adding " » all fields".

    """

    output_nodes = (
        index,
        [desc, ([desc_signature, ([desc_annotation, "validator "],
                                  [desc_addname,
                                   "ValidatorAsteriskRootValidator."],
                                  [desc_name, "check_root"],
                                  [desc_annotation, "  »  "],
                                  [pending_xref, ([emphasis, "all fields"])])],
                [desc_content])
         ]
    )

    # explicit local
    input_rst = [
        '',
        '.. py:pydantic_validator:: ValidatorAsteriskRootValidator.check_root',
        '   :module: target.configuration',
        '   :classmethod:',
        '   :validator-replace-signature: True',
        ''
    ]
    doctree = parse_rst(input_rst)
    assert_node(doctree, output_nodes)


def test_autodoc_pydantic_validator_root_pre(parse_rst):
    """Tests correct modification for root validator with `pre=True` adding
    " » all fields".

    This relates to issue #55.

    """

    output_nodes = (
        index,
        [desc, ([desc_signature, ([desc_annotation, "validator "],
                                  [desc_addname,
                                   "ValidatorAsteriskRootValidator."],
                                  [desc_name, "check_root_pre"],
                                  [desc_annotation, "  »  "],
                                  [pending_xref, ([emphasis, "all fields"])])],
                [desc_content])
         ]
    )

    # explicit local
    input_rst = [
        '',
        '.. py:pydantic_validator:: ValidatorAsteriskRootValidator.check_root_pre',
        '   :module: target.configuration',
        '   :classmethod:',
        '   :validator-replace-signature: True',
        ''
    ]
    doctree = parse_rst(input_rst)
    assert_node(doctree, output_nodes)