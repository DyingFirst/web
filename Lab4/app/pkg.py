import re
def validate_password(oldPasswordSHA2, newPassword, newPasswordSHA2, repeatPassword, password_hash):
    errors = {}
    flash_err = ''
    if oldPasswordSHA2 != password_hash.password_hash:
        flash_err = ('Старый пароль введен неверно', 'danger')
        errors["oldPassword"] = "Старый пароль введен неверно"
    if newPassword != repeatPassword:
        flash_err = ('Пароли не совпадают', 'danger')
        errors["repeatPassword"] = "Пароли не совпадают"
    if newPasswordSHA2 == password_hash.password_hash:
        flash_err = ('Старый и новый пароли совпадают', 'danger')
        errors["newPassword"] = "Старый и новый пароли совпадают"
    if not re.fullmatch(
            r"^(?=.+[a-zа-я])(?=.+[A-ZА-Я])(?=.*\d)(?!.*\s)[a-zA-Zа-яА-Я\d~!?@#$%^&*_\-+()\[\]{}><\\/|\"\'.,:;]{8,128}$",
            newPassword):
        flash_err = ('Новый пароль не сответствует требованиям: не менее 8 символов; не более 128 символов; как минимум одна заглавная и одна строчная буква; только латинские или кириллические буквы; как минимум одна цифра; только арабские цифры; без пробелов; Другие допустимые символы:~ ! ? @ # $ % ^ & * _ - + ( ) [ ] { } > < / \ | \" \' . , : ;',
                     'danger')
        errors[
            "newPassword"] = "Новый пароль не сответствует требованиям: не менее 8 символов; не более 128 символов; как минимум одна заглавная и одна строчная буква; только латинские или кириллические буквы; как минимум одна цифра; только арабские цифры; без пробелов; Другие допустимые символы:~ ! ? @ # $ % ^ & * _ - + ( ) [ ] { } > < / \ | \" \' . , : ;"
    return flash_err, errors


