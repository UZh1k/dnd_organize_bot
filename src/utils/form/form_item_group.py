from dataclasses import dataclass, field
from typing import Type

from src.utils.form.form_text_item import FormTextItem


@dataclass
class FormItemGroup:
    main: Type[FormTextItem]
    side: tuple[Type[FormTextItem]] = field(default_factory=tuple)
