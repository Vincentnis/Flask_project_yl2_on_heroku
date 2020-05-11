from flask_restful import abort, Resource
from data import db_session
from flask import jsonify, request, url_for
from models.users import *
from rest_api.parsers import *
from tests import abort_if_user_not_found, abort_if_user_email_equal_to_new_user_email


class UsersResource(Resource): # ресурс для одной работы
    def get(self, user_id):  # получение информации об одной работе
        abort_if_user_not_found(user_id)
        session = db_session.create_session()
        user = session.query(User).get(user_id)
        return jsonify({'user': user.to_dict(only=('age', 'surname', 'name', 'about',
                                                   "speciality", 'email', 'avatar_url'))})

    def put(self, user_id):  # изменение информации по одной работе функция edit_profile
        args = parser.parse_args()  # парсим аргументы
        session = db_session.create_session()
        abort_if_user_not_found(user_id)
        user = session.query(User).get(user_id)  # получили пользователя
        if args["email"] != user.email:  # если почты не совпадают(решил изменить почту)
            abort_if_user_email_equal_to_new_user_email(args["email"])  # то проверка на уникальность почты
        user.age = args['age']
        user.surname = args['surname']
        user.name = args['name']
        user.speciality = args['speciality']
        user.email = args['email']
        user.about = args['about']
        if args['avatar_url']:  # если добавили фото
            user.avatar_url = args['avatar_url']
        if args['password']:  # если решили изменить пароль
            user.set_password(args['password'])
        session.commit()
        return jsonify({'success': 'OK'})


class UsersListResource(Resource):  # ресурс для списка работ
    def get(self):  # получение всех работ
        session = db_session.create_session()
        users = session.query(User).all()
        return {'users': [user.to_dict(only=('age', 'surname', 'name', 'about',
                                             "speciality", 'email', 'avatar_url')) for user in users]}

    def post(self):  # добавление работы
        args = parser.parse_args()  # парсим аргументы
        session = db_session.create_session()
        abort_if_user_email_equal_to_new_user_email(args["email"])  # проверка на уникальность почты
        user = User(age=args['age'],  # создание пользователя
                    surname=args['surname'],
                    name=args['name'],
                    speciality=args['speciality'],
                    email=args['email'],
                    about=args['about'],
                    avatar_url='http://127.0.0.1:8000/profile/nonavatar.jpg'
                    )
        user.set_password(args['password'])  # добавление захешированного пароля
        session.add(user)
        session.commit()
        return jsonify({'success': "OK"})
