from flask_restful import abort
from data import db_session
from models.users import *
from models.jobs import *
from models.messages import *


def abort_if_user_id_not_equal_to_current_user_id(user_id, current_user_id):
    if user_id != current_user_id:
        abort(403)


def abort_if_user_not_found(user_id):
    session = db_session.create_session()
    user = session.query(User).get(user_id)
    if not user:
        abort(404, message=f"User {user_id} not found")


def abort_if_user_email_equal_to_new_user_email(user_email):
    session = db_session.create_session()
    user = session.query(User).filter(User.email == user_email).first()
    if user:
        abort(500, message=f"User with email {user.email} is already exists")


def abort_if_job_not_found(job_id):
    session = db_session.create_session()
    job = session.query(Jobs).get(job_id)
    if not job:
        abort(404, message=f"Job {job_id} not found")


def abort_if_message_not_found(message_id):
    session = db_session.create_session()
    message = session.query(Message).get(message_id)
    if not message:
        abort(404, message=f"Message {message_id} not found")
