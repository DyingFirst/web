import re
def validate_password(oldPasswordSHA2, newPassword, newPasswordSHA2, repeatPassword, password_hash):
    errors = {}
    flash_err = ''
    if oldPasswordSHA2 != password_hash.password_hash:
        flash_err = 'Старый пароль введен неверно'
        errors["oldPassword"] = "Старый пароль введен неверно"
    if newPassword != repeatPassword:
        flash_err = 'Пароли не совпадают'
        errors["repeatPassword"] = "Пароли не совпадают"
    if newPasswordSHA2 == password_hash.password_hash:
        flash_err = 'Старый и новый пароли совпадают'
        errors["repeatPassword"] = ("Старый и новый пароли совпадают")

    if len(newPassword) < 8:
        flash_err = 'Пароль должен быть не менее 8 символов.'
    elif len(newPassword) > 128:
        flash_err = 'Пароль должен быть не более 128 символов.'

    # Проверка на наличие строчной буквы
    if not re.search(r'[a-zа-я]', newPassword):
        flash_err = 'Пароль должен содержать хотя бы одну строчную букву.'
    # Проверка на наличие заглавной буквы
    if not re.search(r'[A-ZА-Я]', newPassword):
        flash_err = 'Пароль должен содержать хотя бы одну заглавную букву.'

    # Проверка на наличие цифры
    if not re.search(r'\d', newPassword):
        flash_err = 'Пароль должен содержать хотя бы одну цифру.'
    # Проверка на наличие пробелов
    if re.search(r'\s', newPassword):
        flash_err = 'Пароль не должен содержать пробелы.'
    # Проверка на допустимые символы
    if not re.match(r'^[a-zA-Zа-яА-Я\d~!?@#$%^&*_\-+()\[\]{}><\\/|\"\'.,:;]+$', newPassword):
        flash_err = 'Пароль должен содержать только допустимые символы.'

    return flash_err, errors
