from data import db_session  # импорт сессии
from forms_for_page import *  # импорт форм страниц
from models.users import *  # импорт модулей(классов)
from models.jobs import *
from models.categories import *
from models.messages import *
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from flask import Flask, render_template, redirect, request, url_for, send_from_directory
from rest_api import users_resources, jobs_resources, messages_resources
from flask_restful import Api, abort
from werkzeug.utils import secure_filename
from requests import get, post, delete, put
import os
from tests import abort_if_user_id_not_equal_to_current_user_id, \
    abort_if_job_not_found  # тестирующие функции
from rest_api.messages_resources import chats_already_exists  # функция для ресурса сообщений(чатов)





@login_manager.user_loader
def load_user(user_id):  # функция получения авторизованного пользователя
    session = db_session.create_session()
    return session.query(User).get(user_id)


@app.route('/logout')
@login_required
def logout():  # выход из аккаунта
    logout_user()
    return redirect("/")


@app.route('/add_job', methods=['GET', 'POST'])  # оработчик добавления работы
@login_required
def add_job():
    form = JobForm()  # форма
    session = db_session.create_session()  # сессия
    choices = [(category.id - 1, category.name) for category in
               session.query(Category)]  # список кортежей: (значение, заголовок)
    form.select.choices = choices
    if form.validate_on_submit():  # если валидация прошла успешно(нет ошибок заполнения формы)
        post('https://yl-flask-alice.herokuapp.com/api/jobs',  # POST запрос на добавление работы
             json={'header': form.header.data, 'requirements': form.requirements.data,
                   'description': form.description.data,
                   'author': current_user.id, 'form': {'choices': choices,  # список доступных значений
                                                       'select_data': form.select.data,  # выбор пользователя: [0, 2, 3]
                                                       'add_category_data': form.add_category.data,
                                                       # чекбокс на добавление новой работы
                                                       'name_of_category': form.name_of_category.data  # имя категории
                                                       }}).json()
        return redirect('/')  # возвращение на главную страницу
    else:
        print(form.errors)  # если есть ошибки формы - показать
    return render_template('add_job_page.html', title='Adding a job',  # отправляем на сервер шаблон
                           form=form)


@app.route('/edit_job/<int:id>', methods=['GET', 'POST'])  # обработчик для изменения работы(id работы)
@login_required  # шаблон используется тот же что и в add_job, добавляется только инфо о выборе пользователя
def edit_job(id):
    abort_if_job_not_found(id)  # если работы не нашлась - not found
    session = db_session.create_session()
    user_id = session.query(Jobs).get(id).author  # id создателя работы
    abort_if_user_id_not_equal_to_current_user_id(user_id, current_user.id)  # Проверка того, что работу меняет её автор
    form = JobForm()
    categories = session.query(Category)
    choices = [(category.id - 1, category.name) for category in categories]
    form.select.choices = choices
    if request.method == "GET":
        job = get(f'https://yl-flask-alice.herokuapp.com/api/jobs/{id}').json()  # получаем информацию о работе
        form.header.data = job['header']  # заносим её в элементы формы
        form.requirements.data = job['requirements']
        form.description.data = job['description']
        form.select.data = job["categories"]
    if form.validate_on_submit():  # если валидация прошла успешно
        put(f'https://yl-flask-alice.herokuapp.com/api/jobs/{id}',  # PUT запрос на изменение информации о работе
            json={'header': form.header.data, 'requirements': form.requirements.data,
                  'description': form.description.data,
                  'form': {'choices': choices,
                           'select_data': form.select.data,
                           'add_category_data': form.add_category.data,
                           'name_of_category': form.name_of_category.data}}).json()
        return redirect('/')  # возвращение на главную страницу
    else:
        print(form.errors)
    return render_template('add_job_page.html', title='Edit job',  # шаблон тот же, заголовок другой
                           form=form)


@app.route('/delete_job/<int:id>')  # обработчик удаления работы
@login_required
def delete_job(id):
    abort_if_job_not_found(id)  # ошибка если работа не найдена
    session = db_session.create_session()
    user_id = session.query(Jobs).get(id).author
    abort_if_user_id_not_equal_to_current_user_id(user_id,
                                                  current_user.id)  # Проверка того, что работу удаляет её автор
    delete(f'https://yl-flask-alice.herokuapp.com/api/jobs/{id}')  # DELETE запрос на удаление работы
    return redirect('/')


@app.route('/profile', methods=['GET', 'POST'])  # обработчик изменения формы
@login_required
def edit_profile():
    form = MyProfile()  # форма профиля
    if request.method == "GET":
        resp = get(f"https://yl-flask-alice.herokuapp.com/api/users/{current_user.id}").json().get(
            'user')  # получаем данные по одному пользователюиз ресурса UsersResource
        form.surname.data = resp["surname"]  # заносим данные в форму
        form.name.data = resp["name"]
        form.age.data = resp["age"]
        form.speciality.data = resp["speciality"]
        form.about.data = resp["about"]
        form.email.data = resp["email"]
    if form.validate_on_submit():
        if not current_user.check_password(form.check_old_password.data):  # проверка валидности старого пароля
            return render_template('edit_profile.html', title='Edit_profile', form=form,
                                   message_for_password="Incorrect old password")  # неправильный пароль - ошибка
        file = request.files["image"]  # получаем картинку из заголовка запроса
        avatar_url = ''
        if file.filename:  # если файл добавили
            filename = secure_filename(file.filename)  # создаем защищенную версию файла, и берём путь
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))  # сохраняем путь
            """В параметрах url_for файл загруженный из папки(функция upload_filename), 
            имя файла и создание абсолютного путя"""
            avatar_url = str(url_for('upload_filename', filename=filename, _external=True))  # --> url к файлу
        resp = put(f"https://yl-flask-alice.herokuapp.com/api/users/{current_user.id}",  # бновляем данные пользователя
                   json={'surname': form.surname.data,
                         'name': form.name.data,
                         'age': form.age.data,
                         'speciality': form.speciality.data,
                         'email': form.email.data,
                         'about': form.about.data,
                         'password': form.password.data,
                         'avatar_url': avatar_url}).json()
        if resp.get('success'):  # если все прошло успешно - идём на главную страницу
            return redirect('/')
        else:  # если ошибка - возвращаем форму и сообщение ошибки
            return render_template('edit_profile.html', title='Edit_profile', form=form,
                                   message=resp['message'])
    else:
        print(form.errors)
    return render_template('edit_profile.html', title='Edit_profile', form=form)  # шаблон без ошибки


@app.route('/open_chat/<int:receiver_id>', methods=["GET", "POST"])  # обработчик чата
@login_required
def messaging(receiver_id):
    if current_user.id == receiver_id:  # проевряем то что мы отправляем сообщение не себе
        abort(403)
    form = ChatForm()  # форма чата
    if request.method == "GET":
        session = db_session.create_session()
        resp = get("https://yl-flask-alice.herokuapp.com/api/messages", json={'sender': current_user.id,  # получаем переписку
                                                               "receiver": receiver_id}).json()
        receiver = session.query(User).get(receiver_id)  # берём модель пользователя для использования аттрибутов
        return render_template("show_chat.html", title="Chat", messages=resp["mes"],
                               form=form, receiver=receiver)
    if form.validate_on_submit():  # если все прошло успешно
        post("https://yl-flask-alice.herokuapp.com/api/messages", json={'sender': current_user.id,
                                                         "receiver": receiver_id,
                                                         "text": form.text.data})  # POST запрос на добавление работы
        return redirect('#')
    else:
        print(form.errors)


@app.route('/edit_message/<int:message_id>', methods=["GET", "POST"])  # обработчик изменения сообщения
@login_required
def edit_message(message_id):
    form = ChatForm()  # форма чата
    form.submit.label.text = "Edit"  # меняю текст кнопки
    if request.method == "GET":
        resp = get(f"https://yl-flask-alice.herokuapp.com/api/messages/{message_id}").json()  # получаем сообщение
        form.text.data = resp["text"]
        messages = get("https://yl-flask-alice.herokuapp.com/api/messages", json={'sender': current_user.id,  # переписка
                                                                   "receiver": resp["receiver"]}).json()
        session = db_session.create_session()
        return render_template("show_chat.html", title="Chat", messages=messages["mes"],
                               form=form, receiver=session.query(User).get(resp["receiver"]))
    if form.validate_on_submit():
        put(f"https://yl-flask-alice.herokuapp.com/api/messages/{message_id}", json={'text': form.text.data})  # изменяем сообщение
        resp = get(f"https://yl-flask-alice.herokuapp.com/api/messages/{message_id}").json()  # сообщение
        return redirect(f'/open_chat/{resp["receiver"]}')  # идём на обработчик чата и id отправителя как параметр
    else:
        print(form.errors)


@app.route('/delete_message/<int:message_id>')  # обработчик удаления сообщения
@login_required
def delete_message(message_id):
    resp = get(f"https://yl-flask-alice.herokuapp.com/api/messages/{message_id}").json()  # сообщение
    delete(f"https://yl-flask-alice.herokuapp.com/api/messages/{message_id}")  # даляем сообщение
    return redirect(f'/open_chat/{resp["receiver"]}')  # идём на обработчик чата и id отправителя как параметр


@app.route('/chats')  # обработчик чатов
@login_required
def chats():
    session = db_session.create_session()
    chats = [tuple(map(int, chat.split(", "))) for chat in  # список чатов [(receiver, message_id),]
             chats_already_exists(current_user.chats)]
    users = [session.query(User).get(chat[0]) for chat in chats]  # список пользователей, с которыми имеется переписка
    messages = [session.query(Message).get(chat[1]) for chat in chats]  # список сообщений
    return render_template("chats.html", users=users, messages=messages)  # шаблон чатов.


@app.route('/profile/<int:user_id>', methods=['GET'])  # обработчик для просмотра профиля пользователя
def view_profile(user_id):
    form = MyProfile()
    resp = get(f"https://yl-flask-alice.herokuapp.com/api/users/{user_id}").json().get('user')  # получение данных пользователя
    if resp:  # заполнение формы
        form.surname.data = resp["surname"]
        form.name.data = resp["name"]
        form.age.data = resp["age"]
        form.speciality.data = resp["speciality"]
        form.about.data = resp["about"]
        form.email.data = resp["email"]
    else:
        return redirect("/")
    return render_template('view_profile.html', title='View_profile', form=form, file=resp["avatar_url"], id=user_id)


@app.route('/profile/<filename>')
def upload_filename(filename):  # загрузка файла из директории app.config['UPLOAD_FOLDER']
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)


@app.route("/")  # обработчик главной страницы
def main_page():
    session = db_session.create_session()
    jobs = session.query(Jobs)
    return render_template("jobs_list.html", jobs=jobs, title="Main page",  # очередь работ и список их авторов
                           authors=[session.query(User).get(job.author) for job in jobs])


@app.route('/login', methods=['GET', 'POST'])  # обработчик авторизации
def login():
    form = LoginForm()  # форма
    if form.validate_on_submit():
        session = db_session.create_session()
        user = session.query(User).filter(User.email == form.email.data).first()  # ищем пользователя по введённой почте
        if user and user.check_password(form.password.data):  # если и почта и логин подходят - авторизация пользователя
            login_user(user, remember=form.remember_me.data)
            return redirect("/")
        return render_template('login_page.html',  # иначе тот же шаблон, с ошибкой
                               message="Wrong login or password", title='Authorization',
                               form=form)
    return render_template('login_page.html', title='Authorization', form=form)


@app.route('/register', methods=['GET', 'POST'])  # обработчик регистрации
def reqister():
    form = RegisterForm()  # форма
    if form.validate_on_submit():  # При успешной валидации отправляем данные и регистрируем пользователя
        resp = post('https://yl-flask-alice.herokuapp.com/api/users',
                    json={'surname': form.surname.data, 'name': form.name.data,
                          'age': form.age.data, 'speciality': form.speciality.data,
                          'email': form.email.data, 'about': form.about.data,
                          'password': form.password.data})
        print(resp.__dict__)
        print(api.__dict__)
        print(app.__dict__)
        if resp.get('success'):  # если все успешно ==> переходим на страницу авторизации
            return redirect('/login')
        else:
            return render_template('register_page.html', title='Registration', form=form,
                                   message=resp['message'])
    return render_template('register_page.html', title='Registration', form=form)




app = Flask(__name__)  # приложение
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'  # секретный ключ для csrf токена
app.config['UPLOAD_FOLDER'] = 'static\img\\'  # папка куда будут загружаться картинки пользователей
login_manager = LoginManager()
login_manager.init_app(app)
api = Api(app)
db_session.global_init("db/work_db.sqlite")  # создаем движок и подкление к бд
api.add_resource(users_resources.UsersListResource, '/api/users')  # ресурс Пользователей
api.add_resource(users_resources.UsersResource, '/api/users/<int:user_id>')  # ресурс Пользователя
api.add_resource(jobs_resources.JobsListResource, '/api/jobs')  # ресурс Работ
api.add_resource(jobs_resources.JobsResource, '/api/jobs/<int:job_id>')  # ресурс Работы
api.add_resource(messages_resources.MessagesListResource, '/api/messages')  # ресурс Сообщений
api.add_resource(messages_resources.MessagesResource, '/api/messages/<int:message_id>')  # ресурс  Сообщения
print(api.__dict__)
print(app.__dict__)
app.run()  # запуск приложения
