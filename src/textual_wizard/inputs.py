from abc import ABC, abstractmethod
from typing import Optional

from textual.validation import Length, Validator
from textual.widgets import Input
from textual.widgets import Select as _Select
from textual.widgets._input import InputType as InputWidgetType


# Base class for all input types
class InputType(ABC):
    name: str
    label: str

    def __init__(self, name: str, label: str) -> None:
        self.name = name
        self.label = label

    @abstractmethod
    def as_widget(self) -> Input | _Select: ...


# Base class for all input types using an `Input` widget
class BaseText[T](InputType):
    validators: list[Validator]
    placeholder: str
    initial_value: str
    input_type: InputWidgetType
    allow_blank: bool

    def __init__(
        self,
        name: str,
        label: str,
        *,
        validators: Optional[list[Validator]] = None,
        placeholder: Optional[str] = None,
        initial_value: Optional[str] = None,
        allow_blank: bool = True,
    ) -> None:
        super().__init__(name, label)

        if validators is None:
            validators = list()

        self.placeholder = placeholder or initial_value or ""

        self.initial_value = initial_value or ""

        if not allow_blank:
            validators.append(Length(1))

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

    @abstractmethod
    def parse_result(self, value: str) -> T: ...


class Text(BaseText[str]):
    input_type: InputWidgetType = "text"

    def parse_result(self, value: str) -> str:
        return value


class Integer(BaseText[int]):
    input_type: InputWidgetType = "integer"

    def parse_result(self, value: str) -> int:
        return int(value)


class Number(BaseText[float]):
    input_type: InputWidgetType = "number"

    def parse_result(self, value: str) -> float:
        return float(value)


type Option[T] = tuple[str, T]
type OptionList[T] = list[Option[T]]


class Select[T](InputType):
    options: OptionList[T]
    default_value: T
    wid: _Select[T]

    def __init__(
        self,
        name: str,
        label: str,
        *,
        options: OptionList[T],
        default_value: Optional[T] = None,
    ) -> None:
        super().__init__(name, label)

        self.options = options

        if default_value is None:
            default_value = options[0][1]
        self.default_value = default_value

    def as_widget(self) -> _Select:
        wid = _Select[T](
            id=self.name,
            options=self.options,
            allow_blank=False,
            value=self.default_value,
        )

        wid.border_title = self.label

        return wid
