"""This module contains tests for edgecases.

"""
import copy

import pytest
import sphinx.errors
from sphinx.transforms.post_transforms import ReferencesResolver


def test_not_json_compliant(autodocument):
    actual = autodocument(
        documenter='pydantic_model',
        object_path='target.edgecases.NotJsonCompliant',
        options_doc={"model-show-json": True},
        deactivate_all=True)

    assert actual == [
        '',
        '.. py:pydantic_model:: NotJsonCompliant',
        '   :module: target.edgecases',
        '',
        '',
        '   .. raw:: html',
        '',
        '      <p><details  class="autodoc_pydantic_collapsable_json">',
        '      <summary>Show JSON schema</summary>',
        '',
        '   .. code-block:: json',
        '',
        '      {',
        '         "title": "NotJsonCompliant",',
        '         "type": "object",',
        '         "properties": {',
        '            "field": {',
        '               "title": "Field"',
        '            }',
        '         }',
        '      }',
        '',
        '   .. raw:: html',
        '',
        '      </details></p>',
        '',
        ''
    ]


def test_current_module_model(parse_rst):
    """Ensure that using current module does not break any features.

    This relates to issue #12.

    """

    input_rst = ['.. py:currentmodule:: target.example_model',
                 '',
                 '.. autopydantic_model:: ExampleModel',
                 '   :model-show-json: True',
                 '   :model-show-config-member: False',
                 '   :model-show-config-summary: True',
                 '   :model-show-validator-members: False',
                 '   :model-show-validator-summary: False',
                 '   :model-hide-paramlist: True',
                 '   :undoc-members: True',
                 '   :members: True',
                 '   :member-order: alphabetical',
                 '   :model-signature-prefix: pydantic_model',
                 '   :field-list-validators: True',
                 '   :field-doc-policy: both',
                 '   :field-show-constraints: True',
                 '   :field-show-alias: True',
                 '   :field-show-default: True',
                 '   :field-signature-prefix: field',
                 '   :validator-signature-prefix: validator',
                 '   :validator-replace-signature: True',
                 '   :validator-list-fields: True',
                 '   :config-signature-prefix: config',
                 '']

    parse_rst(input_rst,
              conf={"extensions": ["sphinxcontrib.autodoc_pydantic"]})


def test_current_module_settings(parse_rst):
    """Ensure that using current module does not break any features.

    This relates to issue #12.

    """

    input_rst = ['.. py:currentmodule:: target.example_setting',
                 '',
                 '.. autopydantic_settings:: ExampleSettings',
                 '   :settings-show-json: True',
                 '   :settings-show-config-member: False',
                 '   :settings-show-config-summary: True',
                 '   :settings-show-validator-members: False',
                 '   :settings-show-validator-summary: False',
                 '   :settings-hide-paramlist: True',
                 '   :undoc-members: True',
                 '   :members: True',
                 '   :member-order: alphabetical',
                 '   :settings-signature-prefix: pydantic_settings',
                 '   :field-list-validators: True',
                 '   :field-doc-policy: both',
                 '   :field-show-constraints: True',
                 '   :field-show-alias: True',
                 '   :field-show-default: True',
                 '   :field-signature-prefix: field',
                 '   :validator-signature-prefix: validator',
                 '   :validator-replace-signature: True',
                 '   :validator-list-fields: True',
                 '   :config-signature-prefix: config',
                 '']

    parse_rst(input_rst,
              conf={"extensions": ["sphinxcontrib.autodoc_pydantic"]})


def test_any_reference(test_app, monkeypatch):
    """Ensure that `:any:` reference does also work with directives provided
    by autodoc_pydantic.

    This relates to #3.

    """

    failed_targets = set()
    func = copy.deepcopy(ReferencesResolver.warn_missing_reference)

    def mock(self, refdoc, typ, target, node, domain):
        failed_targets.add(target)
        return func(self, refdoc, typ, target, node, domain)

    with monkeypatch.context() as ctx:
        ctx.setattr(ReferencesResolver, "warn_missing_reference", mock)
        app = test_app("edgecase-any-reference")
        app.build()

    assert "does.not.exist" in failed_targets
    assert "target.example_setting.ExampleSettings" not in failed_targets


def test_autodoc_member_order(autodocument):
    """Ensure that member order does not change when pydantic models are used.

    This relates to #21.

    """

    actual = autodocument(
        documenter='module',
        object_path='target.edgecase_member_order',
        options_app={"autodoc_member_order": "bysource"},
        options_doc={"members": None},
        deactivate_all=True)

    assert actual == [
        '',
        '.. py:module:: target.edgecase_member_order',
        '',
        'Module doc string.',
        '',
        '',
        '.. py:pydantic_model:: C',
        '   :module: target.edgecase_member_order',
        '',
        '   Class C',
        '',
        '',
        '.. py:class:: D()',
        '   :module: target.edgecase_member_order',
        '',
        '   Class D',
        '',
        '',
        '.. py:pydantic_model:: A',
        '   :module: target.edgecase_member_order',
        '',
        '   Class A',
        '',
        '',
        '.. py:class:: B()',
        '   :module: target.edgecase_member_order',
        '',
        '   Class B',
        '']


def test_typed_field_reference(test_app, monkeypatch):
    """Ensure that typed fields within doc strings successfully reference
    pydantic models/settings.

    This relates to #27.

    """

    failed_targets = set()
    func = copy.deepcopy(ReferencesResolver.warn_missing_reference)

    def mock(self, refdoc, typ, target, node, domain):
        failed_targets.add(target)
        return func(self, refdoc, typ, target, node, domain)

    with monkeypatch.context() as ctx:
        ctx.setattr(ReferencesResolver, "warn_missing_reference", mock)
        app = test_app("edgecase-typed-field-reference")
        app.build()


def test_json_error_strategy_raise(test_app):
    """Confirm that a non serializable field raises an exception if strategy
    is to raise.

    This relates to #28.

    """

    with pytest.raises(sphinx.errors.ExtensionError):
        conf = {"autodoc_pydantic_model_show_json_error_strategy": "raise"}
        app = test_app("json-error-strategy", conf=conf)
        app.build()


def test_json_error_strategy_warn(test_app, log_capturer):
    """Confirm that a non serializable field triggers a warning during build
    process.

    This relates to #28.

    """

    conf = {"autodoc_pydantic_model_show_json_error_strategy": "warn"}

    with log_capturer() as logs:
        app = test_app("json-error-strategy", conf=conf)
        app.build()

    assert logs[0].msg == (
        "JSON schema can't be generated for 'example.NonSerializable' "
        "because the following pydantic fields can't be serialized properly: "
        "['field']."
    )


def test_json_error_strategy_coerce(test_app, log_capturer):
    """Confirm that a non serializable field triggers no warning during build
    process.

    This relates to #28.

    """

    conf = {"autodoc_pydantic_model_show_json_error_strategy": "coerce"}

    with log_capturer() as logs:
        app = test_app("json-error-strategy", conf=conf)
        app.build()

    assert len(logs) == 0


def test_autodoc_pydantic_model_show_field_summary_not_inherited(autodocument):
    """Ensure that autodoc pydantic respects `:inherited-members:` option when
    listing fields in model/settings. More concretely, fields from base classes
    should not be listed be default.

    This relates to #32.

    """

    result = [
        '',
        '.. py:pydantic_model:: ModelShowFieldSummaryInherited',
        '   :module: target.configuration',
        '',
        '   ModelShowFieldSummaryInherited.',
        '',
        '   :Fields:',
        '      - :py:obj:`field3 (int) <target.configuration.ModelShowFieldSummaryInherited.field3>`',
        ''
    ]

    actual = autodocument(
        documenter='pydantic_model',
        object_path='target.configuration.ModelShowFieldSummaryInherited',
        options_app={"autodoc_pydantic_model_show_field_summary": True},
        deactivate_all=True)
    assert result == actual


def test_autodoc_pydantic_model_show_field_summary_inherited(autodocument):
    """Ensure that autodoc pydantic respects `:inherited-members:` option when
    listing fields in model/settings. More concretely, fields from base classes
    should be listed if `:inherited-members:` is given.

    This relates to #32.

    """
    result = [
        '',
        '.. py:pydantic_model:: ModelShowFieldSummaryInherited',
        '   :module: target.configuration',
        '',
        '   ModelShowFieldSummaryInherited.',
        '',
        '   :Fields:',
        '      - :py:obj:`field1 (int) <target.configuration.ModelShowFieldSummaryInherited.field1>`',
        '      - :py:obj:`field2 (str) <target.configuration.ModelShowFieldSummaryInherited.field2>`',
        '      - :py:obj:`field3 (int) <target.configuration.ModelShowFieldSummaryInherited.field3>`',
        ''
    ]

    actual = autodocument(
        documenter='pydantic_model',
        object_path='target.configuration.ModelShowFieldSummaryInherited',
        options_app={"autodoc_pydantic_model_show_field_summary": True,
                     "autodoc_pydantic_model_members": True},
        options_doc={"inherited-members": "BaseModel"},
        deactivate_all=True)
    assert result == actual


def test_autodoc_pydantic_model_show_validator_summary_inherited(autodocument):
    result = [
        '',
        '.. py:pydantic_model:: ModelShowValidatorsSummaryInherited',
        '   :module: target.configuration',
        '',
        '   ModelShowValidatorsSummaryInherited.',
        '',
        '   :Validators:',
        '      - :py:obj:`check <target.configuration.ModelShowValidatorsSummaryInherited.check>` » :py:obj:`field <target.configuration.ModelShowValidatorsSummaryInherited.field>`',
        '      - :py:obj:`check_inherited <target.configuration.ModelShowValidatorsSummaryInherited.check_inherited>` » :py:obj:`field <target.configuration.ModelShowValidatorsSummaryInherited.field>`',
        ''
    ]

    actual = autodocument(
        documenter='pydantic_model',
        object_path='target.configuration.ModelShowValidatorsSummaryInherited',
        options_app={"autodoc_pydantic_model_show_validator_summary": True,
                     "autodoc_pydantic_model_members": True},
        options_doc={"inherited-members": "BaseModel"},
        deactivate_all=True)
    assert result == actual


def test_autodoc_pydantic_model_show_validator_summary_not_inherited(autodocument):
    result = [
        '',
        '.. py:pydantic_model:: ModelShowValidatorsSummaryInherited',
        '   :module: target.configuration',
        '',
        '   ModelShowValidatorsSummaryInherited.',
        '',
        '   :Validators:',
        '      - :py:obj:`check_inherited <target.configuration.ModelShowValidatorsSummaryInherited.check_inherited>` » :py:obj:`field <target.configuration.ModelShowValidatorsSummaryInherited.field>`',
        ''
    ]

    actual = autodocument(
        documenter='pydantic_model',
        object_path='target.configuration.ModelShowValidatorsSummaryInherited',
        options_app={"autodoc_pydantic_model_show_validator_summary": True,
                     "autodoc_pydantic_model_members": True},
        deactivate_all=True)
    assert result == actual
