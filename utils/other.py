import re

POPULAR_CITIES = (
    "Москва",
    "Санкт-Петербург",
    "Новосибирск",
    "Екатеринбург",
    "Казань",
    "Омск",
)

CITY_TO_TIMEZONE = {
    "Москва": "UTC+3",
    "Санкт-Петербург": "UTC+3",
    "Новосибирск": "UTC+7",
    "Екатеринбург": "UTC+5",
    "Казань": "UTC+3",
    "Омск": "UTC+6",
}

POPULAR_SYSTEMS = (
    "DnD",
    "Pathfinder",
    "GURPS",
    "FATE",
    "Savage Worlds",
    "Зов Ктулху",
    "Warhammer",
    "Cyberpunk",
)

POPULAR_DND_SETTINGS = (
    "Forgotten Realms",
    "Dragonlance",
    "Eberron",
    "Planescape",
    "Ravenloft",
    "Greyhawk",
    "Ravnica",
)

POPULAR_DND_REDACTIONS = ("DnD24", "DnD5e", "DnD3.5e", "DnD3e", "DnD2e", "ADnD", "ODnD")


def generate_simple_choices(
    choices: tuple[str | int, ...]
) -> tuple[tuple[str, str], ...]:
    return tuple((choice, choice) for choice in choices)


def generate_city_choices() -> tuple[tuple[str, str], ...]:
    return generate_simple_choices(POPULAR_CITIES)


def create_tag(string: str) -> str:
    return string.replace(" ", "").replace("-", "").replace("_", "").replace(".", "")


def contains_link(text: str) -> bool:
    # Regex pattern to match URLs, including those without http/https or www
    link_pattern = r"(https?://[^\s]+|www\.[^\s]+|[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})"
    return re.search(link_pattern, text) is not None


def is_command(text: str) -> bool:
    return text.startswith("/")


def utc_to_relative_msk(utc_offset_str: str) -> str:
    msk_offset = 3
    utc_offset = int(utc_offset_str.replace("UTC", ""))

    relative_to_msk = utc_offset - msk_offset

    if relative_to_msk > 0:
        return f"МСК+{relative_to_msk}"
    elif relative_to_msk < 0:
        return f"МСК{relative_to_msk}"
    else:
        return "МСК"
