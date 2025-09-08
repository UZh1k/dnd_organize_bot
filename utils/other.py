import re

POPULAR_CITIES = (
    "Москва",
    "Санкт-Петербург",
    "Новосибирск",
    "Екатеринбург",
    "Казань",
    "Омск",
)

CITY_TAGS = POPULAR_CITIES + (
    "Калининград",
    "Архангельск",
    "Барнаул",
    "Батуми",
    "Белгород",
    "Владивосток",
    "Волгоград",
    "Воронеж",
    "Гагарин",
    "Ижевск",
    "Иркутск",
    "Кемерово",
    "Кострома",
    "Краснодар",
    "Красноярск",
    "Липецк",
    "Минск",
    "Нижний Новгород",
    "Оренбург",
    "Пермь",
    "Ростов-на-Дону",
    "Рязань",
    "Самара",
    "Саратов",
    "Тбилиси",
    "Тольятти",
    "Тюмень",
    "Уфа",
    "Челябинск",
    "Ялта",
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
    "Vampire: The Masquerade",
    "Vampire: The Requiem",
)

POPULAR_SYSTEMS_MAP = {
    "DnD": "DnD",
    "Pathfinder": "Pathfinder",
    "GURPS": "GURPS",
    "FATE": "FATE",
    "Savage Worlds": "Savage Worlds",
    "Зов Ктулху": "Зов Ктулху",
    "Warhammer": "Warhammer",
    "Cyberpunk": "Cyberpunk",
    "VTM": "Vampire: The Masquerade",
    "VTR": "Vampire: The Requiem",
}

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

POPULAR_PLATFORMS = (
    "Foundry VTT",
    "Roll20",
    "DnDBeyond",
    "OwlBear Rodeo",
    "Fantasy grounds VTT",
)


def generate_simple_choices(
    choices: tuple[str | int, ...]
) -> tuple[tuple[str, str], ...]:
    return tuple((choice, choice) for choice in choices)


def generate_city_choices() -> tuple[tuple[str, str], ...]:
    return generate_simple_choices(POPULAR_CITIES)


def create_tag(string: str) -> str:
    return (
        string.replace(" ", "")
        .replace("-", "")
        .replace("_", "")
        .replace(".", "")
        .replace(":", "")
    )


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
