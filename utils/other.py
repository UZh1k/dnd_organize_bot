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
