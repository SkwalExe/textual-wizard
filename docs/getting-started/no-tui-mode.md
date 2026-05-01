# Disabling the TUI

By default, Textual Wizard will render your questions in a modern, fresh-looking TUI (Terminal User Interface).

But you can change this behavior and disable the TUI. Therefore, `Inquierer` will be used to ask for user input, as shown belog.


![No TUI exampe](./no-tui-mode.gif)

To disable the TUI, simply set `disable_tui` to `True` when creating your `Wizard` !

```python
wiz = Wizard(
    MY_QUESTIONS,
    "MyApp",
    disable_tui=True,
)
```
