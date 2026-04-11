import re


def validate_password(password):
    return (8 <= len(password) <= 128 and
                any(c.isupper() for c in password) and
                any(c.islower() for c in password) and
                any(c.isdigit() for c in password) and
                " " not in password)

def validate_username(username):
    return re.match(r'^[a-zA-Z0-9]{5,}$', username)

def validate_user_data(data, is_edit=False):
    errors = {}
    if not is_edit:
        username = data.get('username', '')
        if not validate_username(username):
            errors['username'] = "Логин должен быть от 5 символов (латиница и цифры)."

        password = data.get('password', '')
        if not validate_password(password):
            errors['password'] = "Пароль не соответствует требованиям безопасности."

    if not data.get('first_name'):
        errors['first_name'] = "Имя обязательно для заполнения."
    return errors