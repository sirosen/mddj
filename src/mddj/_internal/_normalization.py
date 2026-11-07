import string

_url_chars_to_remove = string.punctuation + string.whitespace
_url_removal_map = str.maketrans("", "", _url_chars_to_remove)


def normalize_project_url_label(label: str) -> str:
    return label.translate(_url_removal_map).lower()
