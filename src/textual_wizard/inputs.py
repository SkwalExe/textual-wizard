from abc import ABC, abstractmethod
from typing import Generic, Optional, Sequence, TypeVar

import inquirer as inq
from textual.validation import URL as URL_
from textual.validation import Integer as IntegerValidator
from textual.validation import Length, Regex, Validator
from textual.validation import Number as NumberValidator
from textual.widgets import Input, RadioButton
from textual.widgets import RadioSet as RadioSet_
from textual.widgets import Select as Select_
from textual.widgets import SelectionList as SelectionList_
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
    def as_widget(self, qid: str) -> Input | Select_ | SelectionList_ | RadioSet_: ...

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

    def as_widget(self, qid: str) -> Input:
        """Returns a Textual input widget with the corresponding information"""
        wid = Input(
            placeholder=self.placeholder, validators=self.validators, type=self.input_type, id=qid
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

        if not self.allow_blank and len(value) == 0:
            result.failure_reason = "This input cannot be left empty."
            result.valid = False
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


class SelectionList(InputType, Generic[FieldValueType]):
    """
    Allows the user to select multiple options within a predifined list, similar to a checklist.
    """

    options: list[tuple[str, FieldValueType, bool]]
    wid: SelectionList_[FieldValueType]

    def __init__(
        self,
        name: str,
        label: str,
        *,
        options: Sequence[tuple[str, FieldValueType, bool] | tuple[FieldValueType, bool]],
    ) -> None:
        """
        Initializes an instance of this class.

        Args:
            name: The input identifier, used as key in the returned `answers` dict.
            label: The title of the input, displayed to the user.
            options: A list of options that can be selected by the user.
                An option can be represented:
                - by a tuple ("display string", actual_value, is_selected)
                - or the "display string" can be omitted and the value will be converted to a string
        """
        super().__init__(name, label)

        # convert simplified options into 3-sized tuples.
        options_ = list()
        for option in options:
            if len(option) == 2:
                options_ += [(str(option[0]), option[0], option[1])]
            elif len(option) == 3:
                options_ += [option]
            else:
                raise Exception("A SelectionList option should be a tuple of 2 or 3 elements.")

        self.options = options_

    def as_widget(self, qid: str) -> SelectionList_:
        wid = SelectionList_[FieldValueType](
            *self.options,
            id=qid,
        )

        wid.border_title = self.label
        return wid

    def inq_ask(self) -> FieldValueType:
        return inq.checkbox(
            self.label,
            choices=[(x[0], x[1]) for x in self.options],
            default=[x[1] for x in self.options if x[2]],
        )


class Select(InputType, Generic[FieldValueType]):
    """
    Allows the user to select a value within a list of radio buttons
    """

    options: list[tuple[str, FieldValueType]]
    default_value: FieldValueType
    wid: Select_[FieldValueType]

    def __init__(
        self,
        name: str,
        label: str,
        *,
        options: Sequence[tuple[str, FieldValueType] | FieldValueType],
        default_value: Optional[FieldValueType] = None,
    ) -> None:
        """
        Initializes an instance of this class.

        Args:
            name: The input identifier, used as key in the returned `answers` dict.
            label: The title of the input, displayed to the user.
            options: A list of options that can be selected by the user.
                An option can be represented by:
                - any value that can be converted to a string
                - a tuple ("displayed text", actual_value)
            default_value: The default value of the input.
                You must identify the default element by its actual value,
                (the second part of the tuple).
        """
        super().__init__(name, label)

        # Convert simplified options to ("displayed text", actual_value)
        options_ = list()
        for option in options:
            if isinstance(option, tuple):
                options_ += [option]
            else:
                options_ += [(str(option), option)]
        self.options = options_

        if default_value is None:
            default_value = self.options[0][1]

        self.default_value = default_value

    def as_widget(self, qid: str) -> Select_:
        wid = Select_[FieldValueType](
            id=qid,
            options=self.options,
            allow_blank=False,
            value=self.default_value,
        )

        wid.border_title = self.label

        return wid

    def inq_ask(self) -> FieldValueType:
        # We assume inq.list_input will return a good type
        return inq.list_input(self.label, choices=self.options, default=self.default_value)  # type: ignore


class RadioSet(InputType):
    """
    Allows the user to select a value within a predefined list of options.
    """

    options: list[str]
    default_value: str
    wid: RadioSet_

    def __init__(
        self,
        name: str,
        label: str,
        *,
        options: list[str],
        default_value: Optional[str] = None,
    ) -> None:
        """
        Initializes an instance of this class.

        Args:
            name: The input identifier, used as key in the returned `answers` dict.
            label: The title of the input, displayed to the user.
            options: A list of options that can be selected by the user.
                An option is represented by a string.
            default_value: The default value of the input (str).
        """
        super().__init__(name, label)

        self.options = options

        if default_value is None:
            default_value = options[0]
        self.default_value = default_value

    def as_widget(self, qid: str) -> RadioSet_:
        buttons = [RadioButton(x, x == self.default_value) for x in self.options]
        wid = RadioSet_(
            id=qid,
            *buttons,
        )

        wid.border_title = self.label

        return wid

    def inq_ask(self) -> list[str]:
        # We assume inq.list_input will return a good type
        return inq.list_input(self.label, choices=self.options, default=self.default_value)  # type: ignore
