# Creating a basic application

## TL;DR

If you want to get started quickly, check out this script. It covers the basics but doesn't demonstrate all the features of the library. For a comprehensive understanding, read through the entire section. To discover all the available features, take a look at the other documentation modules.

```python
# We import the main class
from textual_wizard import Wizard

# We import the input types we want
from textual_wizard.inputs import Integer, Number, Select, Text

# We define our questions in a list
MY_QUESTIONS = [
    Text("name", "What is your name?", placeholder="John Doe", allow_blank=False),
    Select(
        "animal",
        "What is your favourite animal?",
        options=[
            ("I love dogs 🐶", "dog"),
            ("I love cats 😺", "cat"),
            ("Something else...", "other"),
        ],
    ),
    Integer("pet_count", "How many pets do you have?"),
    Number("height", "How tall are you (in meters)", placeholder="1.70"),
]

# We create the wizard and run it,
# getting the user's inputs in the answers dict
wiz = Wizard(MY_QUESTIONS, "MyApp", "Hello")
answers = wiz.run()

print(f"Your name is {answers['name']}.")
```

## Tutorial

This section will guide you through creating a simple Wizard application in less than 3 minutes.

### Imports

First, import the necessary modules based on the features you need.

```python
# Import the main class (REQUIRED)
from textual_wizard import Wizard

# Import the desired input types.
# These are the only availble types for now, 
# But we are planning on adding new ones soon!
from textual_wizard.inputs import Integer, Number, Select, Text
```

### Defining your questions

To define the questions asked by your application, you must create a list containing input objects:

```python
MY_QUESTIONS = [
    Text("name", "What's your name?", placeholder="John Doe"),
    Integer("pet_count", "How many pets do you have?"),
]
```

### Running the wizard

Instantiate the Wizard class with your questions and some metadata. Then, call the run() method to execute the wizard and retrieve user inputs as a dictionary.

```python
my_wizard = Wizard(MY_QUESTIONS, "App Title", "App Subtitle")
answers = my_wizard.run()

print(f"Your name is {answers['name']}.")
```
