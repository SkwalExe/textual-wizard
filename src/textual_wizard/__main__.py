from rich.console import Console
from rich.panel import Panel
from rich.pretty import pprint
from rich.text import Text as RichText

from textual_wizard import Wizard
from textual_wizard.inputs import Integer, Number, Select, Text


def main() -> None:
    ANIMALS = ["Cats 😺", "Dogs 🐶", "Monkeys 🐵", "Mice 🐭", "Hamsters 🐹", "Bunnies 🐰", "Other"]

    MY_QUESTIONS = [
        Text("name", "What is your name?", placeholder="John Doe", allow_blank=False),
        Select(
            "animal",
            "What is your favourite animal?",
            options=[(option, option) for option in ANIMALS],
        ),
        Integer("pet_count", "How many pets do you have?"),
        Text(
            "email",
            "Your email address (optional)",
            placeholder="me@example.com",
            initial_value="me@example.com",
        ),
        Number("height", "How tall are you (in meters)", placeholder="1.70"),
    ]

    wiz = Wizard(MY_QUESTIONS, "MyApp", "Hello")
    answers = wiz.run()

    console = Console()
    console.print(Panel(RichText.assemble("Result", justify="center", style="bold")))

    pprint(answers, expand_all=True)

if __name__ == "__main__":
    main()

