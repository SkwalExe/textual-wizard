from typing import Any, Optional, Sequence

from textual import on
from textual.app import App, ComposeResult
from textual.containers import Container, Horizontal
from textual.reactive import reactive
from textual.widgets import Button, Header, Input, Label
from textual.widgets import Select as _Select
from textual.widgets._select import NoSelection

from textual_wizard.exceptions import QuestionNameNotUnique
from textual_wizard.inputs import BaseText, InputType, Select, ValidationResult


class WizardApp(App[dict[str, Any]]):
    questions: Sequence[InputType]
    """Questions supplied by the user"""

    answers: dict[str, Any] = dict()
    """Answers to return when the wizard is completed"""

    CSS_PATH = "wizard.tcss"

    # -------------------- Validation error handling
    # Validation of the input is triggered:
    # - On input change
    # - When the next button is clicked

    error_label: Label = Label("", id="error-label", classes="hidden")
    """Widget showing invalid input errors below the input widget"""
    error_text: reactive[str | None] = reactive(None)
    """The description of the currently shown invalid input error"""

    def set_error(self, error: str | None) -> None:
        """Set the input error text for the current input widget"""
        self.error_text = error

    def watch_error_text(self) -> None:
        """Update the error label on the screen when error_text changes"""
        if self.error_text is None:
            # If there is no error, hide the error label,
            # Put the input widget in normal mode
            self.error_label.add_class("hidden")
            self.next_button.disabled = False
            self.active_input.remove_class("invalid")
        else:
            # If there is an error, put the input widget in invalid mode
            # Show the error label and update it's content
            self.active_input.add_class("invalid")
            self.error_label.remove_class("hidden")
            self.error_label.renderable = self.error_text
            self.next_button.disabled = True

    def on_input_changed(self, message: Input.Changed) -> None:
        """Validate the input at every change"""
        if not isinstance(self.selected_question, BaseText):
            raise Exception(
                "Input.Changed is fired if the current input is based on a text field."
                "So we assume the selected question is of type BaseText."
            )

        self.handle_validation_result(self.selected_question.is_value_accepted(message.value))

    def handle_validation_result(self, vr: ValidationResult) -> bool:
        """Handles the result of every input validation"""

        # There is a better way to do that but the linter isnt happy
        if vr.valid:
            self.set_error(None)
            return True
        else:
            self.set_error(vr.failure_reason)
            return False

    def validate_input(self) -> bool:
        """Triggers a validation for the current input"""
        wid = self.active_input

        if isinstance(wid, Input):
            question = self.selected_question
            if not isinstance(question, BaseText):
                raise Exception(
                    "We assume the current question is text based if the current"
                    "widget is a textual Input."
                )
            results = question.is_value_accepted(wid.value)
            return self.handle_validation_result(results)
        # If the current widget is not an Input, it must be a Select, so no validation required.
        return True

    # -------------------- Switching between questions
    back_button: Button = Button("Back", id="back-button", variant="warning", disabled=True)
    next_button: Button = Button("Next", id="next-button", variant="primary")

    question_index: int = 0
    """Index of the current question within self.questions"""

    input_widgets: list[Input | _Select] = list()
    """List of all the input widgets, matching the index of items in self.questions"""

    @property
    def active_input(self) -> Input | _Select:
        return self.input_widgets[self.question_index]

    @property
    def selected_question(self) -> InputType:
        return self.questions[self.question_index]

    def goto(self, question_index: int) -> None:
        """Go to the question with provided index"""
        # Do nothing if we are trying to go to the next question while the input is invalid
        if not self.validate_input() and question_index >= self.question_index:
            return

        # If we are going to a precedent question, clear the error on the current input
        self.set_error(None)

        # Register the value of the input when navigating to the next question
        if question_index >= self.question_index:
            value = None
            if isinstance(self.selected_question, Select):
                value = self.active_input.value
                if isinstance(value, NoSelection):
                    value = None
            elif isinstance(self.selected_question, BaseText) and isinstance(
                self.active_input, Input
            ):
                value = self.selected_question.parse_result(self.active_input.value)
            self.answers[self.selected_question.name] = value

        # If the user clicked next on the last question, return the answers
        if question_index >= len(self.questions):
            self.exit(self.answers)
            return

        # Hide the previous questions
        self.active_input.add_class("hidden")

        self.question_index = question_index

        # Show the new one
        self.active_input.remove_class("hidden")
        self.active_input.focus()

        # Enable the back button if this is not the first question
        self.back_button.disabled = self.question_index == 0

    @on(Button.Pressed, "#next-button")
    def next_question(self) -> None:
        """Go to the next question when the next button is clicked"""
        # go the the next question
        self.goto(self.question_index + 1)

    @on(Button.Pressed, "#back-button")
    def previous_question(self) -> None:
        """Go the the previous question when the back button is clicked"""
        self.goto(self.question_index - 1)

    def on_input_submitted(self, _: Input.Submitted) -> None:
        """Simulate a click on the next button when enter is pressed on an input"""
        self.next_question()

    # --------------------

    def set_questions(self, questions: Sequence[InputType]) -> None:
        self.questions = questions

    def compose(self) -> ComposeResult:
        yield Header()

        with Container():
            for i, question in enumerate(self.questions):
                # Check if the name is not already registered in answers
                if question.name in self.answers:
                    raise QuestionNameNotUnique(
                        "Questions name must be unique but multiple questions "
                        f"named '{question.name}' were supplied."
                    )

                # Get a widget for the input
                _wid = question.as_widget()
                # Initialize the answer as null
                self.answers[question.name] = None
                self.input_widgets.append(_wid)

                # If its not the first input, hide it
                if i != 0:
                    _wid.add_class("hidden")

                yield _wid

            yield self.error_label

            with Horizontal(id="buttons"):
                yield self.back_button
                yield self.next_button


# This class will add a layer of abstraction
# to the textual application
class Wizard:
    """
    Use this class to interface with the library. It allows you to create your wizard and to run it.
    """

    questions: Sequence[InputType]
    wiz_app: WizardApp = WizardApp()
    disable_tui: bool

    def __init__(
        self,
        questions: Sequence[InputType],
        title: str = "Wizard",
        sub_title: Optional[str] = None,
        *,
        disable_tui: bool = False,
    ) -> None:
        """
        Creates an instance of this class.

        Args:
            questions: A list of inputs to show to the user at each step of the wizard.
            title: The name of your wizard.
                Should be something like the name of your application,
                it will be displayed to the user.
            sub_title: A more specific title, for example describing the goal of the wizard.
            disable_tui: Disable the Textual User Interface and use Inquirer instead.
        """
        self.questions = questions
        self.wiz_app.title = title
        self.disable_tui = disable_tui
        if sub_title is not None:
            self.wiz_app.sub_title = sub_title

    def run(self) -> dict[str, Any] | None:
        """Run the app and return answers. Return None if the wizard was cancelled."""

        # If we run with the TUI
        if not self.disable_tui:
            self.wiz_app.set_questions(self.questions)
            return self.wiz_app.run()

        # Without the TUI
        answers = dict()
        for question in self.questions:
            answers[question.name] = question.inq_ask()

        return answers
