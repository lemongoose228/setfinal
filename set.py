from flask import Flask
from flask import request
from secrets import token_hex
from random import randint

class User:
    def __init__(self, id, nickname, password):
        self.id = id
        self.currentroom = -1
        self.nickname = nickname
        self.password = password
        self.token = token_hex(6)

class Room:
    def __init__(self, id):
        self.id = id
        self.players = []
        self.ongoing = True
        self.field = []
        self.cards = []

        self.score = {}

    def addplayer(self, player):
        if player in self.players and player.currentroom == self.id:
            raise ErrorProcessing("Игрок уже в этой игре")

        self.players.append(player)
        self.score[player.nickname] = 0


    def createCards(self):
        id = 0
        for count in range(1, 4):
            for fill in range(1, 4):
                for shape in range(1, 4):
                    for color in range(1, 4):
                        id += 1
                        newCard = Card(id, color, shape, fill, count)
                        self.cards.append(newCard)

    def createField(self, lenght):
        for i in range(lenght):
            cord = randint(0, len(self.cards) - 1)
            self.field.append(self.cards[cord])
            self.cards.remove(self.cards[cord])

    def findCardById(self, id):
        for card in self.field:
            if card.id == id:
                return card

        raise Exception("Карта не найдена")

class Card:
    def __init__(self, id, color, shape, fill, count):
        self.id = id
        self.color = color
        self.shape = shape
        self.fill = fill
        self.count = count
    def cardData(self):
        response = {}
        response["id"] = self.id
        response["color"] = self.color
        response["shape"] = self.shape
        response["fill"] = self.fill
        response["count"] = self.count
        return response


class Game:
    users = []
    rooms = []


    def registr(self, data):
        nickname = data["nickname"]
        password = data["password"]
        id = len(self.users)
        for i in self.users:
            if i.nickname == nickname:
                raise ErrorProcessing("Такой пользователь уже существует")

        newuser = User(id, nickname, password)
        self.users.append(newuser)

        response = {}
        response["accessToken"] = newuser.token
        response["nickname"] = newuser.nickname
        return response


    def login(self, data):
        nickname = data["nickname"]
        password = data["password"]
        for i in self.users:
            if i.nickname == nickname:
                if i.password == password:
                    response = {}
                    response["accessToken"] = i.token
                    response["nickname"] = i.nickname
                    return response
                else:
                    raise ErrorProcessing("Неверный пароль")

        raise ErrorProcessing("Пользователь не зарегистрирован")


    def findRoomById(self, gameid):
        for room in self.rooms:
            if room.id == gameid:
                return room

        raise ErrorProcessing("Такой комнаты не существует")

    def findByToken(self, checktoken):
        for user in self.users:
            if user.token == checktoken:
                return user
        raise ErrorProcessing("Такого пользователя нет")


    def roomlist(self, data):
        token = data["accessToken"]
        user = self.findByToken(token)
        games = []
        response = {}
        for i in self.rooms:
            games.append({"id": i.id})

        response["games"] = games
        return response


    def createRoom(self, data):
        token = data["accessToken"]
        user = self.findByToken(token)
        id = len(self.rooms)
        newroom = Room(id)
        newroom.addplayer(user)
        self.rooms.append(newroom)
        newroom.createCards()

        newroom.createField(12)

        user.currentroom = newroom.id

        response = {}
        response["success"] = True
        response["exception"] = "null"
        response["gameId"] = newroom.id
        return response

    def getField(self, data):
        token = data["accessToken"]
        user = self.findByToken(token)
        room = self.findRoomById(user.currentroom)

        response = {}
        response["cards"] = []
        for card in room.field:
            response["cards"].append(card.cardData())

        response["status"] = room.ongoing
        response["score"] = room.score[user.nickname]
        return response



    def enterRoom(self, data):
        token = data["accessToken"]
        gameid = data["gameId"]
        user = self.findByToken(token)
        room = self.findRoomById(gameid)
        room.addplayer(user)
        user.currentroom = room.id

        response = {}
        response["success"] = True
        response["exception"] = "null"
        response["gameId"] = room.id
        return response

    def pick(self, data):
        token = data["accessToken"]
        cards = data["cards"]
        if len(cards) != 3:
            raise ErrorProcessing("Неверное кол-во карт")
        user = self.findByToken(token)
        room = self.findRoomById(user.currentroom)


        a = room.findCardById(cards[0])
        b = room.findCardById(cards[1])
        c = room.findCardById(cards[2])


        flag = False

        if (a.fill == b.fill == c.fill) or (6 - a.fill - b.fill - c.fill == 0):
            if (a.color == a.color == c.color) or (6 - c.color - b.color - c.color == 0):
                if (a.count == b.count == c.count) or (6 - a.count - b.count - c.count == 0):
                    if (a.shape == b.shape == c.shape) or (6 - a.shape - b.shape - c.shape == 0):
                        flag = True

        response = {}
        if flag == True:
            if len(room.cards) == 0:
                room.ongoing = False
            room.score[user.nickname] = room.score[user.nickname] + 1
            room.field.remove(a)
            room.field.remove(b)
            room.field.remove(c)

            if len(room.field) == 9:
                if len(room.cards) < 3:
                    room.createField(len(room.cards))
                else:
                    room.createField(3)

        response["score"] = room.score[user.nickname]
        response["isSet"] = flag

        return response


    def addCard(self, data):
        token = data["accessToken"]
        user = self.findByToken(token)
        room = self.findRoomById(user.currentroom)

        if len(room.cards) < 3:
            room.createField(len(room.cards))
        else:
            room.createField(3)

        response = {}
        response["success"] = True
        response["exception"] = "null"

        return response

    def scores(self, data):
        token = data["accessToken"]
        user = self.findByToken(token)
        room = self.findRoomById(user.currentroom)

        response = {}

        response["success"] = True
        response["exception"] = "null"

        response["users"] = []
        for name, score in room.score.items():
            response["users"].append({"name": name, "score": score})


        return response


class ErrorProcessing(BaseException):
    def __init__(self, text):
        self.text = text


