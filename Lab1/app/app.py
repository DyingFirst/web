from flask import Flask, render_template
from pkg import posts_list

app = Flask(__name__)
application = app


@app.route("/")
def index():
    return render_template("index.html")

@app.route("/posts")
def posts():
    return render_template("posts.html", title="Посты", posts=posts_list)


@app.route("/posts/<int:index>")
def post(index):
    p = posts_list[index]
    return render_template("post.html", title=p["title"], post=p)


@app.route("/about")
def about():
    return render_template("about.html", title="Об авторе")


if __name__ == "__main__":
    application.run(debug=True)
