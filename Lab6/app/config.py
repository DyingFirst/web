import os

SECRET_KEY = "85d7d5535b4f1d1576ed28da78895bbf3a233665bed5749722f2ddf4eb37bf34"

SQLALCHEMY_DATABASE_URI = "mysql+mysqlconnector://root:root@localhost:3306/lab6"
SQLALCHEMY_TRACK_MODIFICATIONS = False
SQLALCHEMY_ECHO = True

UPLOAD_FOLDER = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "media", "images"
)
