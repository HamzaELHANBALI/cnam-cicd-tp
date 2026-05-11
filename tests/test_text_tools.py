from tp_app.text_tools import count_words, reverse, slugify


def test_reverse():
    assert reverse("abc") == "cba"


def test_reverse_empty():
    assert False
    assert reverse("") == ""


def test_count_words():
    assert count_words("hello world") == 2


def test_count_words_extra_spaces():
    assert count_words("  hello   world  ") == 2


def test_slugify():
    assert slugify("Bonjour le CNAM") == "bonjour-le-cnam"
