from flask_restful import abort, Resource
from data import db_session
from flask import jsonify, request
from models.messages import *
from models.users import *
from rest_api.parsers import *
import datetime
from requests import get
from sqlalchemy import *
from tests import abort_if_message_not_found


class MessagesResource(Resource):
    def get(self, message_id):
        abort_if_message_not_found(message_id)
        session = db_session.create_session()
        message = session.query(Message).get(message_id)
        return jsonify(message.to_dict(only=("text", "receiver")))

    def delete(self, message_id):
        session = db_session.create_session()
        message = session.query(Message).get(message_id)
        user = session.query(User).get(message.sender)
        user1 = session.query(User).get(message.receiver)
        chats = chats_already_exists(user.chats)  # наши чаты из строкового формата в двумерный массив
        chats1 = chats_already_exists(user1.chats)
        messages = get("http://localhost:8000/api/messages", json={'sender': message.sender,
                                                                   "receiver": message.receiver}).json()["mes"]

        for i in range(len(messages)):  # проходим по сообщениям
            if messages[i][0] == message_id and i == len(messages) - 1:  # если это последнее сообщение
                if len(messages) == 1:
                    for j in range(len(chats)):
                        if chats[j].split(", ")[1] == str(message_id):
                            chats.pop(j)  # удаляем чат
                            break
                    for j in range(len(chats1)):
                        if chats1[j].split(", ")[1] == str(message_id):
                            chats1.pop(j)
                            break
                else:
                    for j in range(len(chats)):
                        if chats[j].split(", ")[1] == str(message_id):
                            chats[j] = f'{chats[j].split(", ")[0]}, {str(messages[i - 1][0])}'
                            break  # берём id предпоследнего
                    for j in range(len(chats1)):
                        if chats1[j].split(", ")[1] == str(message_id):
                            chats1[j] = f'{chats1[j].split(", ")[0]}, {str(messages[i - 1][0])}'
                            break
            user.chats = ';'.join(chats)
            user1.chats = ';'.join(chats1)
        session.delete(message)
        session.commit()
        return jsonify({'success': (chats, chats1), 'mes': messages})

    def put(self, message_id):
        args = message_parser.parse_args()
        if args['text']:
            session = db_session.create_session()
            message = session.query(Message).get(message_id)
            message.text = args['text']
            message.date = datetime.datetime.now()
            session.commit()
            return jsonify({'success': 'commit OK'})
        return jsonify({'success': 'OK'})


class MessagesListResource(Resource):
    def get(self):
        session = db_session.create_session()
        args = message_parser.parse_args()
        sender = args['sender']
        receiver = args['receiver']
        """Сначала мы берём сообщения отправленные нами
            Потом нам от отправителя --> |(тоесть or) и вот - последовательный чат переписки готов"""
        mes = session.query(Message).filter(and_(Message.sender == sender, Message.receiver == receiver) |
                                            and_(Message.sender == receiver, Message.receiver == sender))
        mes = [(message.id, message.sender, message.receiver, message.text, message.date.strftime("%H:%M:%S %d.%m.%Y"))
               for message in mes]  # переводим в список для лучшего представления
        return {"mes": mes}

    def post(self):
        args = message_parser.parse_args()
        if args["text"]:
            session = db_session.create_session()
            message = Message()
            message.text = args["text"]
            message.receiver = args["receiver"]
            message.sender = args["sender"]
            message.date = datetime.datetime.now()
            session.add(message)  # добавляю уже чтобы пользоваться message.id
            user = session.query(User).get(args["sender"])  # собственно мы
            user1 = session.query(User).get(args["receiver"])  # наш собеседник
            chats = [chat.split(", ") for chat in
                     chats_already_exists(user.chats)]  # наши чаты из строкового формата в двумерный массив
            chats1 = [chat.split(", ") for chat in chats_already_exists(user1.chats)]  # чаты собеседника
            for chat_index in range(len(chats)):  # смотрю в списке чатов то, есть ли уже чат с этим пользователем
                if chats[chat_index][0] == str(args["receiver"]):  # если есть
                    chats[chat_index][1] = str(message.id)  # добавляю id последнего сообщения
                    chat_to_insert = chats.pop(chat_index)  # забираю чат и переношу в начало
                    chats.insert(0, chat_to_insert)
                    for chat1_index in range(len(chats1)):  # то же самое, но для собеседника
                        if chats1[chat1_index][0] == str(args["sender"]):
                            chats1[chat1_index][1] = str(message.id)
                            chat_to_insert = chats1.pop(chat1_index)
                            chats1.insert(0, chat_to_insert)
                            break
                    break
            else:  # если нет
                chats.insert(0, (str(args["receiver"]), str(message.id)))  # добавляю чат в наш список
                chats1.insert(0, (str(args["sender"]), str(message.id)))  # добавляю чат в список собеседника
            user.chats = ';'.join([', '.join(chat) for chat in chats])  # обновляю инфо о чатах у нас
            user1.chats = ';'.join([', '.join(chat) for chat in chats1])  # обновляю инфо о чатах у собеседника
            session.commit()
            return jsonify({'success': (chats, chats1)})
        return jsonify({'success': "OK"})


def chats_already_exists(chats):  # функция для возврата значений "пусто" если нет чатов у пользователя
    if chats:
        return chats.split(";")
    return []
