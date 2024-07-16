# Introduction

This module will guide you through the process of installing Textual Wizard, and creating a basic application with it.

## Requirements

Textual Wizard requires **Python 3.12** or later, because it leverages the latest features of the programming language.

!!! danger 
    Python 3.12 is very recent, and might not be available in the official repositories of most Linux distributions yet.  This means that a simple `apt install` will not work.
    On debian-based systems, you can use this PPA as a workaround:
    ```bash
    sudo apt-get install software-properties-common
    sudo add-apt-repository ppa:deadsnakes/ppa
    sudo apt-get update
    sudo apt-get install python3.12
    ```

## Installation

You can install textual-wizard from PyPI using the following command:

!!! danger
    Ensure that Python>=3.12 is installed, or the installation will fail.

```bash
pip install textual-wizard
```

## Example application

To verify the installation and explore the capabilities of Textual Wizard, run the example application with the following command:

```bash
textual-wizard
```

![Example application](../demo.gif)
