from typing import Type

from textual_wizard.inputs import URL, BaseText, Email, Integer, Number, Text

INPUTS: list[Type[BaseText]] = [URL, Email, Integer, Number, Text]


def check_validation(inpt: BaseText, *, valid: list[str], invalid: list[str]) -> None:
    for x in valid:
        assert inpt.is_value_accepted(x).valid
    for y in invalid:
        assert not inpt.is_value_accepted(y).valid


def test_email_validation() -> None:
    check_validation(
        Email("", ""),
        valid=["skwal@skwal.net"],
        invalid=["", "skwal@skwal;net", "skwal.net", "abcd123", "skwal@skwal@net.com"],
    )


def test_URL_validation() -> None:
    check_validation(URL("", ""), valid=["https://skwal.net"], invalid=["https:/skwal.net"])


def test_integer_validation() -> None:
    check_validation(Integer("", ""), valid=["0", "1", "100000"], invalid=["two", "1.2"])


def test_number_validation() -> None:
    check_validation(Number("", ""), valid=["0", "1", "6.022", ".98"], invalid=["two"])


def check_text_validation() -> None:
    check_validation(Text("", ""), valid=["Bonjour"], invalid=[])


def test_valid_when_empty() -> None:
    for inpt in INPUTS:
        assert inpt("", "", allow_blank=True).is_value_accepted("").valid
        assert not inpt("", "").is_value_accepted("").valid


def test_parsed_values() -> None:
    tests = [
        (URL("", ""), "https://skwal.net", "https://skwal.net"),
        (Email("", ""), "skwal@skwal.net", "skwal@skwal.net"),
        (Integer("", ""), "10", 10),
        (Number("", ""), "6.022", 6.022),
        (Text("", ""), "Hello", "Hello"),
    ]
    for test in tests:
        assert test[0].parse_result(test[1]) == test[2]


def test_default_parsed_values() -> None:
    tests = [
        (URL("", "", allow_blank=True, default_value="https://skwal.net"), "https://skwal.net"),
        (Email("", "", allow_blank=True, default_value="skwal@skwal.net"), "skwal@skwal.net"),
        (Integer("", "", allow_blank=True, default_value=10), 10),
        (Number("", "", allow_blank=True, default_value=6.022), 6.022),
        (Text("", "", allow_blank=True, default_value="Hello"), "Hello"),
    ]
    for test in tests:
        assert test[0].parse_result("") == test[1]
