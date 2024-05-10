import re
def calculator(a, b, operator):

    result = 0
    if operator == "+":
        result = a + b
    elif operator == "-":
        result = a - b
    elif operator == "*":
        result = a * b
    elif operator == "/":
        result = a / b
    return result

def phone_validate(phone):
    phone_numbers = re.findall("\d{1}", phone)
    if not phone_numbers:
        phone_numbers.append("")

    error = ""
    if not all([symbol in [" ", "(", ")", "-", ".", "+", *list(map(str, list(range(10))))] for symbol in phone]):
        error = "Недопустимый ввод. В номере телефона встречаются недопустимые символы."
    elif phone_numbers[0] in ["7", "8"] and len(phone_numbers) != 11:
        error = "Недопустимый ввод. Неверное количество цифр."
    elif phone_numbers[0] not in ["7", "8"] and len(phone_numbers) != 10:
        error = "Недопустимый ввод. Неверное количество цифр."

    if len(phone_numbers) == 10:
        phone_numbers.insert(0, "8")

    return phone_numbers, error