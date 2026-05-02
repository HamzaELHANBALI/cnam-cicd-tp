"""Petits utilitaires de manipulation de texte."""


def reverse(text: str) -> str:
    return text[::-1]


def count_words(text: str) -> int:
    return len(text.split())


def slugify(text: str) -> str:
    return text.strip().lower().replace(" ", "-")
