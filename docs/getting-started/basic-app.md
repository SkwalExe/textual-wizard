# Creating a basic application

## TL;DR

If you want to get started quickly, check out this script. It covers the basics but doesn't demonstrate all the available features. For a comprehensive understanding, read through the entire section. To discover all the available features, take a look at the other documentation pages.

```python
# We import the main class
from textual_wizard import Wizard

# We import the input types we want
from textual_wizard.inputs import URL, Email, Integer, RadioSet, Select, Text

ANIMALS = ["Cats 😺", "Dogs 🐶", "Monkeys 🐵", "Mice 🐭", "Hamsters 🐹", "Bunnies 🐰", "Other"]
DAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

# We define our questions in a list
MY_QUESTIONS = [
    Text(
        # the first argument will be used as a dictionnary key in the answers dict.
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
    URL(
        "github_url",
        "What is the URL of your Github ?",
        placeholder="https://github.com/SkwalExe",
        allow_blank=True,
    ),
    Email("email", "What is your email ?", placeholder="me@domain.com", allow_blank=True),
    RadioSet(
        "radio_set",
        "What day of the week were you born ?",
        options=DAYS,
    ),
]

# We create the wizard
wiz = Wizard(MY_QUESTIONS, "MyApp", "Hello")
# and we run it, getting the user's inputs in the answers dict
answers = wiz.run()

print(f"Your name is {answers['name']}.")
```

## Tutorial

This section will guide you through creating a simple Wizard application in less than 3 minutes.

### Imports

First, import the necessary modules based on the features you need.

```python
# Import the main class
from textual_wizard import Wizard

# Import the desired input types.
# These aren't only availble types !
from textual_wizard.inputs import Integer, Text
```

### Defining your questions

To define the questions asked by your application, you must create a list containing input objects:

```python
MY_QUESTIONS = [
    Text("name", "What's your name?", placeholder="John Doe"),
    Integer("finger_count", "How many fingers do you have?"),
]
```

### Running the wizard

Instantiate the Wizard class with your questions and some metadata. Then, call the run() method to execute the wizard and retrieve user inputs as a dictionary.

```python
my_wizard = Wizard(MY_QUESTIONS, "App Title", "App Subtitle")
answers = my_wizard.run()

print(f"Your name is {answers['name']}.")
```
