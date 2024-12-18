from models import User, UserTypeText, UserType


def get_user_text(user: User):
    user_role = UserTypeText[UserType(user.user_type).name].value
    return (
        f"Имя: {user.name}\n"
        f"Возраст: {user.age}\n"
        f"Город: {user.city.name}\n"
        f"Часовой пояс: {user.timezone}\n"
        f"Роль в НРИ: {user_role}\n"
        f"Об себе: {user.bio}"
    )
