from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_required, current_user
from sqlalchemy.exc import IntegrityError
from models import db, Course, Category, User, Review
from tools import CoursesFilter, ImageSaver

bp = Blueprint("courses", __name__, url_prefix="/courses")

COURSE_PARAMS = ["author_id", "name", "category_id", "short_desc", "full_desc"]


def params():
    return {p: request.form.get(p) or None for p in COURSE_PARAMS}


def search_params():
    return {
        "name": request.args.get("name"),
        "category_ids": [x for x in request.args.getlist("category_ids") if x],
    }


@bp.route("/")
def index():
    courses = CoursesFilter(**search_params()).perform()
    pagination = db.paginate(courses)
    courses = pagination.items
    categories = db.session.execute(db.select(Category)).scalars()
    return render_template(
        "courses/index.html",
        courses=courses,
        categories=categories,
        pagination=pagination,
        search_params=search_params(),
    )


@bp.route("/new")
@login_required
def new():
    course = Course()
    categories = db.session.execute(db.select(Category)).scalars()
    users = db.session.execute(db.select(User)).scalars()
    return render_template(
        "courses/new.html", categories=categories, users=users, course=course
    )


@bp.route("/create", methods=["POST"])
@login_required
def create():
    f = request.files.get("background_img")
    img = None
    course = Course()
    try:
        if f and f.filename:
            img = ImageSaver(f).save()

        image_id = img.id if img else None
        course = Course(**params(), background_image_id=image_id)
        db.session.add(course)
        db.session.commit()
    except IntegrityError as err:
        flash(
            f"Возникла ошибка при записи данных в БД. Проверьте корректность введённых данных. ({err})",
            "danger",
        )
        db.session.rollback()
        categories = db.session.execute(db.select(Category)).scalars()
        users = db.session.execute(db.select(User)).scalars()
        return render_template(
            "courses/new.html", categories=categories, users=users, course=course
        )

    flash(f"Курс {course.name} был успешно добавлен!", "success")

    return redirect(url_for("courses.index"))


@bp.route("/<int:course_id>")
def show(course_id):
    course = db.get_or_404(Course, course_id)
    reviews = (
        db.session.query(Review, User)
        .join(Review, Review.user_id == User.id)
        .order_by(Review.created_at.desc())
        .limit(5)
    )

    self_review = ""
    if current_user.is_authenticated:
        self_review = (
            db.session.query(Review, User)
            .join(Review, Review.user_id == User.id)
            .filter(User.id == current_user.id)
            .first()
        )

    return render_template(
        "courses/show.html",
        course_id=course_id,
        course=course,
        reviews=reviews,
        self_review=self_review,
    )


@bp.route("/send-review/<int:course_id>", methods=["POST"])
@login_required
def send_review(course_id):
    try:
        reviews = db.session.execute(
            db.select(Review).filter_by(course_id=course_id)
        ).scalars()

        reviewRatingSum = 0
        reviewRatingNum = 0
        currentUserReviewFlag = False
        for review in reviews:
            reviewRatingSum += review.rating
            reviewRatingNum += 1
            if review.user_id == current_user.id:
                currentUserReviewFlag = True

        if currentUserReviewFlag:
            flash("Вы уже оставляли отзыв к этому курсу!", "warning")
            return redirect(url_for("courses.show", course_id=course_id))

        review = Review(
            rating=request.form.get("rating"),
            text=request.form.get("text") or "",
            course_id=course_id,
            user_id=current_user.id,
        )
        db.session.add(review)
        db.session.commit()

        course = db.get_or_404(Course, course_id)
        course.rating_sum = reviewRatingSum + review.rating
        course.rating_num = reviewRatingNum + 1
        db.session.commit()

        flash("Ваш отзыв был успешно добавлен!", "success")
    except Exception as e:
        flash(f"Возникла ошибка при добавлении отзыва. ({e})", "danger")
    return redirect(url_for("courses.show", course_id=course_id))


@bp.route("<int:course_id>/delete-review/<int:review_id>")
@login_required
def delete_review(course_id, review_id):
    try:
        review = db.session.execute(db.select(Review).filter_by(id=review_id)).scalar()

        if not review:
            flash("Отзыв не найден!", "warning")
            return redirect(url_for("courses.show", course_id=course_id))

        if review.user_id != current_user.id:
            flash("Вы не можете удалить этот отзыв!", "warning")
            return redirect(url_for("courses.show", course_id=course_id))

        db.session.delete(review)
        db.session.commit()

        reviews = db.session.execute(
            db.select(Review).filter_by(course_id=course_id)
        ).scalars()

        reviewRatingSum = 0
        reviewRatingNum = 0
        for review in reviews:
            reviewRatingSum += review.rating
            reviewRatingNum += 1
        course = db.get_or_404(Course, course_id)
        course.rating_sum = reviewRatingSum
        course.rating_num = reviewRatingNum
        db.session.commit()

        flash("Ваш отзыв был успешно удален!", "success")
    except Exception as e:
        flash(f"Возникла ошибка при удалении отзыва. ({e})", "danger")
    return redirect(url_for("courses.show", course_id=course_id))


@bp.route("<int:course_id>/reviews", methods=["GET", "POST"])
def reviews(course_id):
    if request.method == "POST":
        sort_order = request.form.get("sort_order", "newness")
    else:
        sort_order = request.args.get("sort_order", "newness")

    if sort_order == "newness":
        reviews = (
            db.session.query(Review, User)
            .join(Review, Review.user_id == User.id)
            .order_by(Review.created_at.desc())
        )
    elif sort_order == "positive":
        reviews = (
            db.session.query(Review, User)
            .join(Review, Review.user_id == User.id)
            .order_by(Review.rating.desc())
        )
    elif sort_order == "negative":
        reviews = (
            db.session.query(Review, User)
            .join(Review, Review.user_id == User.id)
            .order_by(Review.rating.asc())
        )

    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 4, type=int)

    pagination = reviews.paginate(page=page, per_page=per_page)
    reviews = pagination.items

    self_review = ""
    if current_user.is_authenticated:
        self_review = (
            db.session.query(Review, User)
            .join(Review, Review.user_id == User.id)
            .filter(User.id == current_user.id)
            .first()
        )

    return render_template(
        "courses/reviews.html",
        pagination=pagination,
        course_id=course_id,
        reviews=reviews,
        self_review=self_review,
        sort_order=sort_order,
    )
