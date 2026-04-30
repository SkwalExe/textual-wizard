from random import random
from typing import Any

from click_extra import command, option
from rich.console import Console
from rich.panel import Panel
from rich.pretty import pprint
from rich.text import Text as RichText
from textual.validation import Number as Nb

from textual_wizard import Wizard
from textual_wizard.inputs import URL, Email, Integer, Number, RadioSet, Select, SelectionList, Text


@command(params=None, version_fields={"prog_name": "Textual Wizard"})
@option(
    "-t", "--disable-tui", is_flag=True, help="Disable the Textual TUI and use Inquirer instead."
)
def textual_wizard(disable_tui: bool) -> None:
    ANIMALS = ["Cats 😺", "Dogs 🐶", "Monkeys 🐵", "Mice 🐭", "Hamsters 🐹", "Bunnies 🐰", "Other"]

    MY_QUESTIONS = [
        Text(
            "my_text_field",
            "Please type in any text!",
            placeholder="(This is a placeholder!!)",
            allow_blank=True,
        ),
        Select(
            "animal",
            "What is your favourite animal?",
            options=[(option, option) for option in ANIMALS],
        ),
        Integer(
            "my_integer",
            "This is an integer input field!",
            placeholder="1337",
            allow_blank=True,
        ),
        URL("url", "URL input field!", placeholder="https://skwal.net", allow_blank=True),
        Email("email", "Email address input field!", placeholder="me@domain.com", allow_blank=True),
        Number(
            "number",
            "This is a number field, with validators!",
            placeholder="This is a placeholder.",
            validators=[Nb(5, 10)],
            allow_blank=True,
        ),
        SelectionList(
            "selection_list",
            "What animals did you see in the last month ?",
            options=[(x, x, random() < 0.3) for x in ANIMALS],
        ),
        RadioSet(
            "radio_set",
            "Select a friend.",
            options=ANIMALS,
        ),
    ]
    answers: dict[str, Any] | None = dict()
    wiz = Wizard(MY_QUESTIONS, "MyApp", "Example Application", disable_tui=disable_tui)
    answers = wiz.run()

    console = Console()
    console.print(Panel(RichText.assemble("Result", justify="center", style="bold")))

    pprint(answers, expand_all=True)
