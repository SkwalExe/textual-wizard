# The Wizard class

This wizard class is your main interface with the library. In other words, you must use it to interact with TW (TextualWizard) in order to create, run, and retrieve user input from your wizard.

The usage is very straightforward, considering that you can create and run your wizard in just two steps.

1. First, you create your wizard, and supply basic information.

```python
my_wizard = Wizard(
    questions=[Text(...), Integer(...), Number(...), Select(...)],
    title="MyAwesomeApplication",
    sub_title="Account creation"
)
```

1. Then, just run it!

```python
answers = my_wizard.run()
```

![Preview](../demo.gif)

---

::: textual_wizard.Wizard
