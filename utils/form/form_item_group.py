from dataclasses import dataclass, field

from utils.form.form_text_item import FormTextItem


@dataclass
class FormItemGroup:
    main: type[FormTextItem]
    side: tuple[type[FormTextItem], ...] = field(default_factory=tuple)
