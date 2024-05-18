from flask import Flask, render_template, make_response, request, flash
from pkg import calculator, phone_validate

app = Flask(__name__)

application = app
app.secret_key = "85d7d5535b4f1d1576ed28da78895bbf3a233665bed5749722f2ddf4eb37bf34"

@app.route('/')
def index():
    return render_template('index.html')


@app.route('/url')
def url():
    return render_template('url.html', title="Параметры URL", )


@app.route('/headers')
def headers():
    return render_template('headers.html', title="Заголовки")


@app.route('/cookies')
def cookies():
    resp = make_response(render_template('cookies.html', title="Куки"))
    if 'user' in request.cookies:
        resp.delete_cookie('user')
    else:
        resp.set_cookie('user', 'admin')
    return resp


@app.route('/forms', methods=['GET', 'POST'])
def forms():
    # if request.method == "POST"
    return render_template('forms.html', title="Параметры формы")


@app.route('/calc')
def calc():
    a = float(request.args.get('a', 0))
    b = float(request.args.get('b', 0))
    operator = request.args.get('operator')
    result = calculator(a, b, operator)

    return render_template('calc.html', title="Калькулятор", result=result)


@app.route("/phoneNumber", methods=["POST", "GET"])
def phoneNumber():
    if request.method == 'POST':
        phone = request.form["phone"]

        phone_number, error = phone_validate(phone)

        if error:
            flash(error, 'danger')
            return render_template("phoneNumber.html", title="Проверка номера телефона", phone=phone)


        return render_template("phoneNumber.html", title="Проверка номера телефона", phone="8-{1}{2}{3}-{4}{5}{6}-{7}{8}-{9}{10}".format(*phone_number))
    else:
        return render_template("phoneNumber.html", title="Проверка номера телефона")

if __name__ == "__main__":
    application.run(debug=True)
