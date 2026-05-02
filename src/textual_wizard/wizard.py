from typing import Any, Optional, ReadOnly, Sequence, TypedDict

from textual import on
from textual.app import App, ComposeResult
from textual.containers import Container, Horizontal
from textual.reactive import reactive
from textual.widget import Widget
from textual.widgets import Button, Header, Input, Label, RadioButton
from textual.widgets import RadioSet as RadioSet_
from textual.widgets import Select as Select_
from textual.widgets import SelectionList as SelectionList_
from textual.widgets._select import NoSelection

from textual_wizard.exceptions import QuestionNameNotUnique
from textual_wizard.inputs import BaseText, InputType, ValidationResult


class WizardApp(App[dict[str, Any]]):
    questions: Sequence[InputType]
    """Questions supplied by the user"""

    answers: dict[str, Any]
    """Answers to return when the wizard is completed"""

    single_page: bool
    """Show all the questions on a single page"""

    allow_back: bool = False
    """
    Allow the user to click the previous button while on the first question,
    which will return None, and set go_back.
    """

    go_back: bool
    """
    True if back button was clicked while on the first question.
    Used to go back to the previous stage.
    """

    CSS_PATH = "wizard.tcss"

    # -------------------- Validation error handling
    # Validation of the input is triggered:
    # - On input change
    # - When the next button is clicked

    error_labels: list[Label]
    """Widgets showing invalid input errors below the input widgets"""

    error_texts: reactive[list[str | None]] = reactive([])
    """The description of the currently shown invalid input errors"""

    def set_error(self, error: str | None, index: int) -> None:
        """Set the input error text for the current input widget"""
        self.error_texts[index] = error
        self.error_texts_updated()

    def error_texts_updated(self) -> None:
        """Update the error labels on the screen when an element inside error_labels changes."""
        next_button_disabled = False

        for i, error_text in enumerate(self.error_texts):
            if error_text is None:
                # If there is no error, hide the error label,
                # Put the input widget in normal mode
                self.error_labels[i].add_class("hidden")
                self.input_widgets[i].remove_class("invalid")
            else:
                # If there is an error, put the input widget in invalid mode
                # Show the error label and update it's content
                self.input_widgets[i].add_class("invalid")
                self.error_labels[i].remove_class("hidden")
                self.error_labels[i].update(error_text)
                next_button_disabled = True
        self.next_button.disabled = next_button_disabled

    def on_input_changed(self, message: Input.Changed) -> None:
        """Validate the input at every change"""
        qid = self.get_question_id(message.input)
        if qid is None:
            raise Exception("Encountered an input widget with id None")

        question = self.questions[qid]
        if isinstance(question, BaseText):
            self.handle_validation_result(question.is_value_accepted(message.value), qid)

    def handle_validation_result(self, vr: ValidationResult, qid: int) -> bool:
        """Handles the result of every input validation"""

        # There is a better way to do that but the linter isnt happy
        if vr.valid:
            self.set_error(None, qid)
            return True

        self.set_error(vr.failure_reason, qid)
        return False

    def validate_current_input(self) -> bool:
        """Triggers a validation for the current input"""
        if self.single_page:
            raise Exception("validate_current_input should not be called in single_page mode.")
        return self.validate_input(self.question_index)

    def validate_input(self, qid: int) -> bool:
        """Triggers a validation for the given question ID"""
        wid = self.input_widgets[qid]

        if isinstance(wid, Input):
            question = self.questions[qid]
            if not isinstance(question, BaseText):
                raise Exception(
                    "We assume the current question is text based if the current"
                    "widget is a textual Input."
                )
            results = question.is_value_accepted(wid.value)
            return self.handle_validation_result(results, self.question_index)
        # If the current widget is not an Input, it must be a Select, so no validation required.
        return True

    def validate_all_inputs(self) -> bool:
        result = True
        for i in range(len(self.questions)):
            result = result and self.validate_input(i)

        return result

    # -------------------- Switching between questions
    back_button: Button
    next_button: Button

    question_index: int = 0
    """Index of the current question within self.questions"""

    input_widgets: list[Input | Select_ | SelectionList_ | RadioSet_]
    """List of all the input widgets, matching the index of items in self.questions"""

    @property
    def active_input(self) -> Input | Select_ | SelectionList_ | RadioSet_:
        if self.single_page:
            raise Exception("active_input should not be called in single_page mode.")
        return self.input_widgets[self.question_index]

    @property
    def selected_question(self) -> InputType:
        if self.single_page:
            raise Exception("selected_question should not be called in single_page mode.")
        return self.questions[self.question_index]

    def register_input(self, qid: int) -> None:
        """Registers the value of the input at the provided index into self.answers"""
        value: Any = None
        wid = self.input_widgets[qid]
        question = self.questions[qid]
        if isinstance(wid, Select_):
            value = wid.value
            if isinstance(value, NoSelection):
                value = None
        elif isinstance(wid, SelectionList_):
            value = wid.selected
        elif isinstance(wid, RadioSet_) and wid._selected is not None:
            value = str(wid.query(RadioButton)[wid._selected].label)
        elif isinstance(question, BaseText) and isinstance(wid, Input):
            value = question.parse_result(wid.value)

        self.answers[question.name] = value

    def register_all_inputs(self) -> None:
        """Registers the value of all the inputs into self.answers"""
        for i in range(len(self.questions)):
            self.register_input(i)

    def goto(self, question_index: int) -> None:
        """Go to the question with provided index"""
        if self.single_page:
            raise Exception("goto should not be called in single_page mode.")

        # Do nothing if we are trying to go to the next question while the input is invalid
        if not self.validate_current_input() and question_index >= self.question_index:
            return

        # If we are going to a precedent question, clear the error on the current input
        self.set_error(None, self.question_index)

        # Register the value of the input when navigating to the next question
        if question_index >= self.question_index:
            self.register_input(self.question_index)

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

        # Enable the back button if this is not the first question, or if allow_back is enabled
        self.back_button.disabled = (self.question_index == 0) and (not self.allow_back)

    @on(Button.Pressed, "#next-button")
    def next_button_pressed(self) -> None:
        if self.single_page:
            if self.validate_all_inputs():
                self.register_all_inputs()
                self.exit(self.answers)
            return

        self.next_question()

    def next_question(self) -> None:
        """Go to the next question when the next button is clicked or an input is 'submitted'"""
        if self.single_page:
            self.simulate_key("tab")
            return

        # go the the next question
        self.goto(self.question_index + 1)

    @on(Button.Pressed, "#back-button")
    def back_button_pressed(self) -> None:
        if self.allow_back and (self.single_page or self.question_index == 0):
            self.go_back = True
            self.exit(None)
            return

        self.previous_question()

    def previous_question(self) -> None:
        """Go the the previous question when the back button is clicked"""
        self.goto(self.question_index - 1)

    def on_input_submitted(self, _: Input.Submitted) -> None:
        """Simulate a click on the next button when enter is pressed on an input"""
        self.next_question()

    # --------------------

    def set_questions(self, questions: Sequence[InputType]) -> None:
        self.questions = questions

    def get_question_id(self, wid: Widget) -> int | None:
        """Return the question id associated with an input widget"""
        if wid.id is None:
            return None
        id_parts = wid.id.split("-")
        if len(id_parts) != 2:
            return None
        return int(id_parts[1])

    def compose(self) -> ComposeResult:
        # We need to define class properties that are references here to
        # avoid keeping previous objects when creating a new wizard.
        self.answers = dict()
        self.go_back = False
        self.input_widgets = list()
        self.back_button = Button(
            "Back", id="back-button", variant="warning", disabled=(not self.allow_back)
        )
        self.next_button = Button("Next", id="next-button", variant="primary")
        self.error_labels = list()
        self.error_texts = list()

        yield Header()

        with Container():
            yield Label(self.sub_title, id="label-step")
            for i, question in enumerate(self.questions):
                # Check if the name is not already registered in answers
                if question.name in self.answers:
                    raise QuestionNameNotUnique(
                        "Questions name must be unique but multiple questions "
                        f"named '{question.name}' were supplied."
                    )

                # Get a widget for the input
                _wid = question.as_widget(f"input-{i}")
                _wid.add_class("input")
                # Initialize the answer as null
                self.answers[question.name] = None
                self.input_widgets.append(_wid)

                # Only show the first input is single_page is disabled
                if i != 0 and not self.single_page:
                    _wid.add_class("hidden")

                yield _wid
                error_label = Label("", classes="hidden error-label")
                self.error_labels += [error_label]
                self.error_texts += [None]
                yield error_label

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
    wiz_app: WizardApp
    disable_tui: bool
    title: str
    sub_title: Optional[str]

    def __init__(
        self,
        title: str = "Wizard",
        sub_title: Optional[str] = None,
        *,
        disable_tui: bool = False,
        single_page: bool = False,
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
            single_page: Show all the questions on the same page.
        """
        self.wiz_app.single_page = single_page
        self.disable_tui = disable_tui
        self.title = title
        self.sub_title = sub_title

    def run(
        self,
        questions: Sequence[InputType],
    ) -> dict[str, Any] | None:
        """Run the app and return answers. Return None if the wizard was cancelled."""

        self.questions = questions

        # If we run with the TUI
        if not self.disable_tui:
            self.wiz_app = WizardApp()
            self.wiz_app.title = self.title
            if self.sub_title is not None:
                self.wiz_app.sub_title = self.sub_title

            self.wiz_app.set_questions(self.questions)
            return self.wiz_app.run()

        # Without the TUI
        answers = dict()
        for question in self.questions:
            answers[question.name] = question.inq_ask()

        return answers


class WizardStage(TypedDict):
    title: ReadOnly[str]
    questions: ReadOnly[Sequence[InputType]]


Stages = Sequence[WizardStage]


class MultiStageWizard:
    """
    This class allows you to create more complex wizards, with multiple stages.
    """

    disable_tui: bool
    single_page: bool
    title: str

    def __init__(
        self,
        title: str = "Wizard",
        *,
        disable_tui: bool = False,
        single_page: bool = True,
    ) -> None:
        """
        Creates an instance of this class.

        TODO::
        Args:
            title: The name of your wizard.
                Should be something like the name of your application,
                it will be displayed to the user.
            disable_tui: Disable the Textual User Interface and use Inquirer instead.
            single_page: Show all the questions on the same page.
        """

        self.disable_tui = disable_tui
        self.single_page = single_page
        self.title = title

    def run(self, stages: Sequence[WizardStage]) -> dict[str, Any] | None:
        """
        Run the multistage wizard and return answers. Return None if the wizard was cancelled.

        Args:
            stages: A list containing the different stages of your wizard.
                A stage is a dictionnary with the following keys:
                - questions: an array of questions
                - title: the title of your stage
        """

        # If we run with the TUI
        if not self.disable_tui:
            answers = dict()
            stage_i = 0
            while stage_i < len(stages):
                stage = stages[stage_i]
                wiz = WizardApp()
                wiz.single_page = self.single_page
                wiz.title = self.title
                wiz.set_questions(stage["questions"])
                wiz.sub_title = stage["title"]
                if stage_i > 0:
                    wiz.allow_back = True

                stage_answers = wiz.run()
                if stage_answers is None:
                    if wiz.go_back:
                        stage_i -= 1
                        continue
                    return None
                stage_i += 1
                answers.update(stage_answers)

            return answers

        # Without the TUI
        answers = dict()
        for stage in stages:
            print(stage["title"])
            for question in stage["questions"]:
                answers[question.name] = question.inq_ask()

        return answers
