from random import random

from click_extra import command, option
from rich.console import Console
from rich.panel import Panel
from rich.pretty import pprint
from rich.text import Text as RichText
from textual.validation import Number as Nb

from textual_wizard.inputs import URL, Email, Integer, Number, RadioSet, Select, SelectionList, Text
from textual_wizard.wizard import MultiStageWizard, Stages


@command(params=None, version_fields={"prog_name": "Textual Wizard"})
@option(
    "-t",
    "--disable-tui",
    is_flag=True,
    help="Disable the Textual TUI and use Inquirer instead.",
)
@option(
    "-s",
    "--single-page",
    is_flag=True,
    help="Show all the questions on the same page.",
)
def textual_wizard(disable_tui: bool, single_page: bool) -> None:
    ANIMALS = ["Cats 😺", "Dogs 🐶", "Monkeys 🐵", "Mice 🐭", "Hamsters 🐹", "Bunnies 🐰", "Other"]
    DAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

    MY_QUESTIONS: Stages = [
        {
            "title": "First stage",
            "questions": [
                Text(
                    "name",
                    "What is your name ?",
                    placeholder="John Doe",
                    allow_blank=False,
                ),
                Select(
                    "favorite_animal",
                    "What are your favorite animals ?",
                    options=ANIMALS,
                ),
                Integer(
                    "favorite_number",
                    "What is your favorite number ?",
                    placeholder="1337",
                    allow_blank=True,
                ),
            ],
        },
        {
            "title": "Second stage",
            "questions": [
                URL(
                    "github_url",
                    "What is the URL of your Github ?",
                    placeholder="https://github.com/SkwalExe",
                    allow_blank=True,
                ),
                Email(
                    "email",
                    "What is your email ?",
                    placeholder="me@domain.com",
                    allow_blank=True,
                ),
                Number(
                    "favorite_hour",
                    "What is your favorite hour of the day ?",
                    placeholder="16",
                    validators=[Nb(0, 23)],
                    allow_blank=True,
                ),
                SelectionList(
                    "favorite_days",
                    "What days of the week do you like the most ?",
                    options=[(x, x, random() < 0.3) for x in DAYS],
                ),
                RadioSet(
                    "radio_set",
                    "What day of the week were you born ?",
                    options=DAYS,
                ),
            ],
        },
    ]
    wiz = MultiStageWizard(
        "MyApp",
        disable_tui=disable_tui,
        single_page=single_page,
    )
    answers = wiz.run(MY_QUESTIONS)

    console = Console()
    console.print(Panel(RichText.assemble("Result", justify="center", style="bold")))

    pprint(answers, expand_all=True)
