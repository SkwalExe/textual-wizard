from abc import ABC, abstractmethod
from typing import Generic, Optional, TypeVar

import inquirer as inq
from textual.validation import URL as URL_
from textual.validation import Integer as IntegerValidator
from textual.validation import Length, Regex, Validator
from textual.validation import Number as NumberValidator
from textual.widgets import Input
from textual.widgets import Select as _Select
from textual.widgets._input import InputType as InputWidgetType

EMAIL_REGEX = r"^([^\x00-\x20\x22\x28\x29\x2c\x2e\x3a-\x3c\x3e\x40\x5b-\x5d\x7f-\xff]+|\x22([^\x0d\x22\x5c\x80-\xff]|\x5c[\x00-\x7f])*\x22)(\x2e([^\x00-\x20\x22\x28\x29\x2c\x2e\x3a-\x3c\x3e\x40\x5b-\x5d\x7f-\xff]+|\x22([^\x0d\x22\x5c\x80-\xff]|\x5c[\x00-\x7f])*\x22))*\x40([^\x00-\x20\x22\x28\x29\x2c\x2e\x3a-\x3c\x3e\x40\x5b-\x5d\x7f-\xff]+|\x5b([^\x0d\x5b-\x5d\x80-\xff]|\x5c[\x00-\x7f])*\x5d)(\x2e([^\x00-\x20\x22\x28\x29\x2c\x2e\x3a-\x3c\x3e\x40\x5b-\x5d\x7f-\xff]+|\x5b([^\x0d\x5b-\x5d\x80-\xff]|\x5c[\x00-\x7f])*\x5d))*$"  # noqa: E501


class ValidationResult:
    valid: bool = True
    failure_reason: str


# Base class for all input types
class InputType(ABC):
    name: str
    label: str

    def __init__(self, name: str, label: str) -> None:
        self.name = name
        self.label = label

    @abstractmethod
    def as_widget(self) -> Input | _Select: ...

    @abstractmethod
    def inq_ask(self) -> ...: ...


FieldValueType = TypeVar("FieldValueType")


# Base class for all input types using an `Input` widget
class BaseText(InputType, Generic[FieldValueType]):
    validators: list[Validator]
    placeholder: str
    initial_value: str
    input_type: InputWidgetType
    allow_blank: bool
    additional_validators: Optional[list[Validator]] = None
    default_value: FieldValueType

    def __init__(
        self,
        name: str,
        label: str,
        *,
        validators: Optional[list[Validator]] = None,
        placeholder: Optional[str] = None,
        initial_value: Optional[str] = None,
        allow_blank: bool = False,
        default_value: Optional[FieldValueType] = None,
    ) -> None:
        """
        Initializes an instance of this class.

        Args:
            name: The input identifier, used as key in the returned `answers` dict.
            label: The title of the input, displayed to the user.
            validators: A list of Textual validators,
                allowing the user to pass to the next question or displaying an error.
            placeholder: Placeholder for the text field.
            initial_value: Initial value entered in the input.
            allow_blank: Whether or not the text field is considered valid when is it empty.
            default_value: The value returned by the input if allow_blank is
                set to True and the input is empty.
        """
        super().__init__(name, label)

        if validators is None:
            validators = list()
        if self.additional_validators is not None:
            validators += self.additional_validators

        self.placeholder = placeholder or initial_value or ""
        if default_value is not None:
            self.default_value = default_value
        self.initial_value = initial_value or ""

        if not allow_blank:
            validators.append(Length(1, failure_description="You must provide a value."))

        self.validators = validators
        self.allow_blank = allow_blank

    def as_widget(self) -> Input:
        """Returns a Textual input widget with the corresponding information"""
        wid = Input(
            id=self.name,
            placeholder=self.placeholder,
            validators=self.validators,
            type=self.input_type,
        )
        wid.border_title = self.label
        wid.value = self.initial_value
        return wid

    def inq_ask(self) -> FieldValueType:
        """
        Asks a question using Inquirer instead of the Textual User Interface.
        """
        while True:
            answer = inq.text(self.label, default=self.initial_value)
            validation = self.is_value_accepted(answer)
            if not validation.valid:
                print(validation.failure_reason)
                continue
            return self.parse_result(answer)

    def is_value_accepted(self, value: str) -> ValidationResult:
        """
        Determine if a value satisfies all the validators configured on the question.

        Args:
            value: The value your want to check the validity of.
        """
        result = ValidationResult()
        if self.allow_blank and len(value) == 0:
            return result
        for validator in self.validators:
            validation = validator.validate(value)
            if not validation.is_valid:
                result.failure_reason = validation.failure_descriptions[0]
                result.valid = False
                return result

        return result

    def parse_result(self, value: str) -> FieldValueType:
        if len(value) == 0 and self.allow_blank:
            return self.default_value
        return self._parse_result(value)

    @abstractmethod
    def _parse_result(self, value: str) -> FieldValueType: ...


class Text(BaseText[str]):
    """
    Input widget allowing text to be entered without any restrictions.
    """

    input_type: InputWidgetType = "text"
    default_value: str = ""

    def _parse_result(self, value: str) -> str:
        return value


class Email(Text):
    """
    The email input field behaves like a normal text input field,
    but simply adds an email validator.
    """

    additional_validators = [
        Regex(
            EMAIL_REGEX,
            failure_description="Must be a valid email address.",
        )
    ]


class URL(Text):
    """
    The URL input field behaves like a normal text input field,
    but simply adds an URL validator.
    """

    additional_validators = [URL_()]


class Integer(BaseText[int]):
    """
    Allows the user to input an integer.
    Only entering digits will work, other keypresses will just be ignored.
    """

    default_value: int = 0
    input_type: InputWidgetType = "integer"
    additional_validators = [IntegerValidator()]

    def _parse_result(self, value: str) -> int:
        return int(value)


class Number(BaseText[float]):
    """
    Allows the user to input an number.
    Only entering digits and `.` will work, other keypresses will just be ignored.
    """

    default_value: float = 0
    input_type: InputWidgetType = "number"
    additional_validators = [NumberValidator()]

    def _parse_result(self, value: str) -> float:
        return float(value)


# Option[T]: tuple[str, T]
# OptionList[T]: list[Option[T]]


class Select(InputType, Generic[FieldValueType]):
    """
    Allows the user to select a value within a predefined list of options.
    """

    options: list[tuple[str, FieldValueType]]
    default_value: FieldValueType
    wid: _Select[FieldValueType]

    def __init__(
        self,
        name: str,
        label: str,
        *,
        options: list[tuple[str, FieldValueType]],
        default_value: Optional[FieldValueType] = None,
    ) -> None:
        """
        Initializes an instance of this class.

        Args:
            name: The input identifier, used as key in the returned `answers` dict.
            label: The title of the input, displayed to the user.
            options: A list of options that can be selected by the user.
            default_value: The default value of the input.
                You must specify an element by its __return value__
                (the second thingy in the option tuple).
        """
        super().__init__(name, label)

        self.options = options

        if default_value is None:
            default_value = options[0][1]
        self.default_value = default_value

    def as_widget(self) -> _Select:
        wid = _Select[FieldValueType](
            id=self.name,
            options=self.options,
            allow_blank=False,
            value=self.default_value,
        )

        wid.border_title = self.label

        return wid

    def inq_ask(self) -> FieldValueType:
        # We assume inq.list_input will return a good type
        return inq.list_input(self.label, choices=self.options, default=self.default_value)  # type: ignore
