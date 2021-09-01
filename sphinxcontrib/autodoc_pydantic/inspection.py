"""This module contains inspection functionality for pydantic models.

"""
import functools
import pydoc
from collections import defaultdict
from itertools import chain
from typing import NamedTuple, Tuple, List, Dict, Any, Set, TypeVar, Iterator

import pydantic
from pydantic import BaseModel, create_model
from pydantic.class_validators import Validator
from pydantic.fields import ModelField, UndefinedType
from sphinx.addnodes import desc_signature


class ValidatorFieldMap(NamedTuple):
    """Contains single mapping of a pydantic validator and field.

    """

    field: str
    validator: str
    is_asterisk: bool
    model_path: str

    def _get_ref(self, name: str) -> str:
        """Create reference for given `name` while prefixing it with model
        path.

        """

        return f"{self.model_path}.{name}"

    @property
    def field_ref(self):
        """Create reference to field object.

        """

        if self.is_asterisk:
            return self.model_path

        return self._get_ref(self.field)

    @property
    def validator_ref(self):
        """Create reference to validator object.

        """

        return self._get_ref(self.validator)


class StaticInspector:
    """Namespace under `ModelInspector` for static methods.

    """

    @staticmethod
    def is_pydantic_model(obj: Any) -> bool:
        """Determine if object is a valid pydantic model.

        """

        if isinstance(obj, type):
            return issubclass(obj, BaseModel)
        return False

    @classmethod
    def is_validator_by_name(cls, name: str, obj: Any) -> bool:
        """Determine if a validator is present under provided `name` for given
        `model`.

        """

        if cls.is_pydantic_model(obj):
            wrapper = ModelWrapper.factory(obj)
            return name in wrapper.get_validator_names()
        return False


class BaseInspectionComposite:
    """Serves as base class for inspector composites which are coupled to
    `ModelInspector` instances. Each composite provides a separate namespace to
    handle different areas of pydantic models (e.g. fields and validators).

    """

    def __init__(self, parent: 'ModelInspector'):
        self._parent = parent
        self.model = self._parent.model


class FieldInspector(BaseInspectionComposite):
    """Provide namespace for inspection methods for fields of pydantic models.

    """

    def __init__(self, parent: 'ModelInspector'):
        super().__init__(parent)
        self.attribute = self.model.__fields__

    @property
    def validator_names(self) -> Dict[str, Set[str]]:
        """Return mapping between all field names (keys) and their
        corresponding validator names (values).

        """

        standard = self.validator_names_standard
        root = self.validator_names_root

        # add root names
        complete = standard.copy()
        asterisk = complete.get("*", set()).union(root["*"])
        complete["*"] = asterisk

        return complete

    @property
    def validator_names_root(self) -> Dict[str, Set[str]]:
        """Return mapping between all field names (keys) and their
        corresponding validator names (values) for root validators only.

        """

        root_validator_names = self._parent.validators.names_root_validators
        return {"*": root_validator_names}

    @property
    def validator_names_standard(self) -> Dict[str, List[str]]:
        """Return mapping between all field names (keys) and their
        corresponding validator names (values) for standard validators only.

        Please be aware, the asterisk field name `*` is used to represent all
        fields.

        """

        validators_attribute = self._parent.validators.attribute
        name_getter = self._parent.validators.get_names_from_wrappers

        return {field: name_getter(validators)
                for field, validators in validators_attribute.items()}

    @property
    def names(self) -> List[str]:
        """Return field names while keeping ordering.

        """

        return list(self.attribute.keys())

    def get(self, name: str) -> ModelField:
        """Get the instance of `ModelField` for given field `name`.

        """

        return self.attribute[name]

    def get_property_from_field_info(self, field_name: str,
                                     property_name: str) -> Any:
        """Get specific property value from pydantic's field info.

        """

        field = self.get(field_name)
        return getattr(field.field_info, property_name, None)

    def is_required(self, field_name: str) -> bool:
        """Check if a given pydantic field is required/mandatory. Returns True,
        if a value for this field needs to provided upon model creation.

        """

        types_to_check = (UndefinedType, type(...))
        default_value = self.get_property_from_field_info(
            field_name=field_name,
            property_name="default")

        return isinstance(default_value, types_to_check)

    def is_json_serializable(self, field_name: str) -> bool:
        """Check if given pydantic field is JSON serializable by calling
        pydantic's `model.json()` method. Custom objects might not be
        serializable and hence would break JSON schema generation.

        """

        field = self.get(field_name)

        class Cfg:
            arbitrary_types_allowed = True

        try:
            field_args = (field.type_, field.default)
            model = create_model("_", test_field=field_args, Config=Cfg)
            model.schema()
            return True
        except Exception:
            return False

    @property
    def non_json_serializable(self) -> List[str]:
        """Get all fields that can't be safely serialized.

        """

        return [name for name in self.names
                if not self.is_json_serializable(name)]


class ConfigInspector(BaseInspectionComposite):
    """Provide namespace for inspection methods for config class of pydantic
    models.

    """

    def __init__(self, parent: 'ModelInspector'):
        super().__init__(parent)
        self.attribute: Dict = self.model.Config

    @property
    def items(self) -> Dict:
        """Return all non private (without leading underscore `_`) items of
        pydantic configuration class.

        """

        return {key: getattr(self.attribute, key)
                for key in dir(self.attribute)
                if not key.startswith("_")}


class ValidatorInspector(BaseInspectionComposite):
    """Provide namespace for inspection methods for validators of pydantic
    models.

    """

    def __init__(self, parent: 'ModelInspector'):
        super().__init__(parent)
        self.attribute: Dict = self.model.__validators__

    @staticmethod
    def get_names_from_wrappers(validators: Iterator[Validator]) -> Set[str]:
        """Return the actual validator names as defined in the class body from
        list of pydantic validator wrappers.

        Parameters
        ----------
        validators: list
            Wrapper objects for pydantic validators.

        """

        return {validator.func.__name__ for validator in validators}

    @property
    def names_root_validators(self) -> Set[str]:
        """Return all names of root validators.

        """

        def get_name_from_root(validators):
            return {validator[1].__name__ for validator in validators}

        pre_root = get_name_from_root(self.model.__pre_root_validators__)
        post_root = get_name_from_root(self.model.__post_root_validators__)

        return pre_root.union(post_root)

    @property
    def names_asterisk_validators(self) -> Set[str]:
        """Return all names of asterisk validators. Asterisk are defined as
        validators, that process all availble fields. They consist of root
        validators and validators with the `*` field target.

        """

        asterisk_validators = self.attribute.get("*", [])
        asterisk = self.get_names_from_wrappers(asterisk_validators)
        return asterisk.union(self.names_root_validators)

    @property
    def names_standard_validators(self) -> Set[str]:
        """Return all names of standard validators which do not process all
        fields at once (in contrast to asterisk validators).

        """

        validator_wrappers = chain.from_iterable(self.attribute.values())
        names_all_validators = self.get_names_from_wrappers(validator_wrappers)
        return names_all_validators.difference(self.names_asterisk_validators)

    @property
    def names(self) -> Set[str]:
        """Return names of all validators of pydantic model.

        """

        asterisks = self.names_asterisk_validators
        standard = self.names_standard_validators

        return asterisks.union(standard)

    def is_asterisk(self, name: str) -> bool:
        """Check if provided validator `name` references an asterisk validator.

        Parameters
        ----------
        name: str
            Name of the validator.

        """

        return name in self.names_asterisk_validators


class SchemaInspector(BaseInspectionComposite):
    """Provide namespace for inspection methods for general properties of
    pydantic models.

    """

    @property
    def sanitized(self) -> Dict:
        """Get model's `schema` while handling non serializable fields. Such
        fields will be replaced by TypeVars.

        """

        try:
            return self.model.schema()
        except (TypeError, ValueError):
            new_model = self.create_sanitized_model()
            return new_model.schema()

    def create_sanitized_model(self) -> BaseModel:
        """Generates a new pydantic model from the original one while
        substituting invalid fields with typevars.

        """

        invalid_fields = self._parent.fields.non_json_serializable
        new = {name: (TypeVar(name), None) for name in invalid_fields}
        return create_model(self.model.__name__, __base__=self.model, **new)


class ReferenceInspector(BaseInspectionComposite):
    """Provide namespace for inspection methods for creating references
    mainly between pydantic fields and validators.

    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        mappings_asterisk = self._create_mappings_asterisk()
        mappings_standard = self._create_mappings_standard()
        self.mappings = mappings_standard.union(mappings_asterisk)

    @property
    def model_path(self) -> str:
        """Retrieve the full path of the model.

        """

        return f"{self.model.__module__}.{self.model.__name__}"

    def create_model_reference(self, name: str) -> str:
        """Create reference for given attribute `name` returning full path
        including the model path.

        """

        return f"{self.model_path}.{name}"

    def _create_mappings_asterisk(self) -> Set[ValidatorFieldMap]:
        """Generate `ValidatorFieldMap` instances for asterisk validators.

        """

        field_validator_names = self._parent.fields.validator_names
        asterisk_validators = field_validator_names.pop("*")
        model_path = self.model_path

        return {ValidatorFieldMap(field="all fields",
                                  validator=validator,
                                  is_asterisk=True,
                                  model_path=model_path)
                for validator in asterisk_validators}

    def _create_mappings_standard(self) -> Set[ValidatorFieldMap]:
        """Generate `ValidatorFieldMap` instances for asterisk validators.

        """

        is_asterisk = self._parent.validators.is_asterisk
        field_validator_names = self._parent.fields.validator_names
        model_path = self.model_path

        references = set()
        for field, validators in field_validator_names.items():
            refs = {ValidatorFieldMap(field=field,
                                      validator=validator,
                                      is_asterisk=False,
                                      model_path=model_path)
                    for validator in validators
                    if not is_asterisk(validator)}
            references.update(refs)

        return references

    def filter_by_validator_name(self, name: str) -> List[ValidatorFieldMap]:
        """Return mappings for given validator `name`.

        """

        return [mapping for mapping in self.mappings
                if mapping.validator == name]

    def filter_by_field_name(self, name: str) -> List[ValidatorFieldMap]:
        """Return mappings for given field `name`.

        """

        return [mapping for mapping in self.mappings
                if mapping.field in (name, "all fields")]


class ModelInspector:
    """Provides inspection functionality for pydantic models.

    """

    static = StaticInspector

    def __init__(self, model: BaseModel):
        self.model = model
        self.config = ConfigInspector(self)
        self.schema = SchemaInspector(self)
        self.fields = FieldInspector(self)
        self.validators = ValidatorInspector(self)
        self.references = ReferenceInspector(self)

    @classmethod
    def from_signode(cls, signode: desc_signature) -> "ModelInspector":
        """Create instance from a `signode` as used within sphinx directives.

        """

        model_name = signode["fullname"].split(".")[0]
        model = pydoc.locate(f"{signode['module']}.{model_name}")
        return cls(model)


class ModelWrapper:
    """Wraps pydantic models and provides additional inspection functionality
    on top of it.

    Parameters
    ----------
    model: pydantic.BaseModel
        The pydantic model for which validators field validator_field_mappings
        will be extracted.

    """

    CACHED: Dict[int, "ModelWrapper"] = {}

    def __init__(self, model: BaseModel):
        self.model = model
        self.wrapper = ModelInspector(model)

    def get_model_path(self) -> str:  # DONE
        """Retrieve the full path to given model.

        """

        return self.wrapper.references.model_path

    def get_field_validator_names(self) -> Dict[str, Set[str]]:  # DONE
        """Retrieve function names from pydantic Validator wrapper objects.

        """

        return self.wrapper.fields.validator_names

    def get_fields(self) -> List[str]:  # Done
        """Retrieves all fields from pydantic model.

        """

        return self.wrapper.fields.names

    def get_validator_names(self) -> Set[str]:  # Done
        """Collect all names of the validator functions.

        """

        return self.wrapper.validators.names

    def get_reference(self, name: str):  # Done
        """Create reference path to given name.

        """

        return self.wrapper.references.create_model_reference(name)

    @classmethod
    def factory(cls, model: BaseModel) -> "ModelWrapper":
        """Factory with caching ability to prevent recreation of new instances.

        """

        model_id = id(model)
        result = cls.CACHED.get(model_id)
        if result:
            return result

        mapping = ModelWrapper(model)
        cls.CACHED[model_id] = mapping
        return mapping

    @classmethod
    def from_signode(cls, signode: desc_signature) -> "ModelWrapper":
        """Create instance from a `signode` as used within sphinx directives.

        """

        model_name = signode["fullname"].split(".")[0]
        model = pydoc.locate(f"{signode['module']}.{model_name}")
        return cls.factory(model)

    def get_fields_for_validator(self,
                                 validator_name: str) -> List[
        ValidatorFieldMap]:
        """Return all fields for a given validator.

        """

        return self.wrapper.references.filter_by_validator_name(
            validator_name)

    def get_validators_for_field(self, field_name: str) -> List[
        ValidatorFieldMap]:
        """Return all validators for given field.

        """

        return self.wrapper.references.filter_by_field_name(
            field_name)

    def get_field_object_by_name(self, field_name: str) -> ModelField:
        """Return the field object for given field name.

        """
        return self.wrapper.fields.get(field_name)

    def get_field_property(self, field_name: str, property_name: str) -> Any:
        """Return a property of a given field.

        """

        return self.wrapper.fields.get_property_from_field_info(field_name,
                                                                property_name)

    def field_is_required(self, field_name: str) -> bool:
        """Check if a field is required.

        """

        return self.wrapper.fields.is_required(field_name)

    def find_non_json_serializable_fields(self) -> List[str]:
        """Get all fields that can't be safely serialized.

        """

        return self.wrapper.fields.non_json_serializable

    def get_safe_schema_json(self) -> Dict:
        """Get model's `schema_json` while handling non serializable fields.

        """

        return self.wrapper.schema.sanitized
