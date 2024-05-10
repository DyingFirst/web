"use strict";
window.onload = function () {
    const phoneNumberInput = document.querySelector("#phone-number-input");
    if (phoneNumberInput.value == "Недопустимый ввод. Неверное количество цифр." || phoneNumberInput.value == "Недопустимый ввод. В номере телефона встречаются недопустимые символы.") {
        phoneNumberInput.classList.add("is-invalid");
    }
    else if (/\d-\d{3}-\d{3}-\d{2}-\d{2}/g.test(phoneNumberInput.value)) {
        phoneNumberInput.classList.add("is-valid");
    }
};
