import socket
import json
from message_client import *


class ClientT:
    def __init__(self, host, port, alias):
        self.sock = socket.socket(socket.AF_INET)
        self.sock.connect((host, port))
        self.send_message(MessageRegisterOnClient(alias))
        self.index = None
        self.players = {}
        self.mafia = False
        self.is_vote = False

    def on_message(self, msg):
        is_vote = False
        command = msg["command"]
        args = msg["args"] if "args" in msg else None
        if command == "registered":
            self.index = args["index"]
        elif command == "ready":
            self.mafia = args["mafia"]
            print("\n")
            print("Ты %s" % ("мафия ><" if self.mafia else "мирный житель :)"))
        elif command == "players":
            players = args["players"]
            self.players = {}
            for player in players:
                self.players[player["index"]] = player["alias"]
        elif command == "targets":
            is_vote = True
            for target in args["targets"]:
                print("%d. %s" % (target, self.players[target]))
        elif command == "vote":
            if args["player"] == self.index:
                self.is_vote = False
        elif command == "revote":
            print("\n Было одинаковое число голосов.")
            print("\n ГОЛОСУЕМ СНОВА!")
        elif command == "kill":
            if args["index"] == self.index:
                print("\n ТЕБЯ УБИЛИ :(")
            else:
                print("Убили игрока с именем: %s" % self.players[args["index"]])
        elif command == "finished":
            print("%s победили" % ("Мафия" if args["mafia"] else "Мирные жители"))
        elif command == "chat":
            print("Chat %s: %s" % (args["index"], args["msg"]))
        elif command == "state":
            state = args["state"]
            if state == 1:
                print("\n ДЕНЬ. ГОРОД ГОЛОСУЕТ.")
            elif state == 2:
                print("\n НОЧЬ. МАФИЯ ГОЛОСУЕТ")
            elif state == 3:
                print("\nИГРА ЗАВЕРШЕНА")
        elif command == "err":
            print("ОШИБКА: %s" % args["msg"])
            is_vote = self.is_vote
        elif command == "accepted":
            print("Ваш голос принят.")
        if is_vote:
            self.is_vote = True
            print(self.players[self.index], ", введите цифру игрока из списка, за которого хотите проголосовать.")
            self.send_message(MessageVoteOnClient(input("> ")))

    def send_message(self, msg):
        msg = msg.to_string()
        self.sock.send(int.to_bytes(len(msg), 4, "big") + str.encode(msg))

    def start(self):
        print("Клиентское приложение запущено.")
        while True:
            try:
                msg_len = int.from_bytes(self.sock.recv(4), "big")
                msg = self.sock.recv(msg_len)
                self.on_message(json.loads(msg.decode()))
            except:
                print("Отключен.")
                break


if __name__ == '__main__':
    alias = input("Имя: ")
    client = ClientT("localhost", 1080, alias)
    client.start()
