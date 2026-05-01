# Using single page mode

By default, Textual Wizard will show one question after another, and let the user navigate between them using the `Previous` and `Next` buttons.

But you can change this behavior and use `single page mode`. In single page mode, all the questions are displayed at the same time, as shown below.


![Single page example](./single-page-mode.gif)

To enable single page mode, simply set `single_page` to `True` when creating your `Wizard` !

```python
wiz = Wizard(
    MY_QUESTIONS,
    "MyApp",
    single_page=True,
)
```
