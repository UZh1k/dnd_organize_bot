import re

POPULAR_CITIES = (
    "Москва",
    "Санкт-Петербург",
    "Новосибирск",
    "Екатеринбург",
    "Казань",
)

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


def generate_simple_choices(choices: tuple[str, ...]) -> tuple[tuple[str, str], ...]:
    return tuple((choice, choice) for choice in choices)


def generate_city_choices() -> tuple[tuple[str, str], ...]:
    return generate_simple_choices(POPULAR_CITIES)


def create_tag(string: str) -> str:
    return string.replace(" ", "").replace("-", "").replace("_", "")


def contains_link(text: str) -> bool:
    # Regex pattern to match URLs, including those without http/https or www
    link_pattern = r"(https?://[^\s]+|www\.[^\s]+|[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})"
    return re.search(link_pattern, text) is not None


def is_command(text: str) -> bool:
    return text.startswith("/")
