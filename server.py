import random
import socket
import threading
import functools
import json
from enum import IntEnum
from message_server import *

PLAYERS_FOR_READY = 8
MAFIA_COUNT = 2


class ClientOnServer:
    def __init__(self, conn, addr):
        self.conn = conn
        self.addr = addr

    def recv(self):
        msg_len = 0
        while True:
            try:
                msg_len = self.conn.recv(1)[0]
                break
            except:
                pass
        res = ""
        while True:
            res += self.conn.recv(msg_len).decode()
            msg_len -= len(res)
            if (msg_len == 0):
                break
        return res

    def send(self, msg):
        msg_json = msg.to_string()
        print("Sending message to '" + self.to_string() + "': " + msg_json)
        self.conn.send(int.to_bytes(len(msg_json), 4, "big") + str.encode(msg_json))

    def to_string(self):
        return self.addr[0] + ":" + str(self.addr[1])


class Player:
    def __init__(self, client, alias, index):
        self.client = client
        self.alias = alias
        self.index = index
        self.alive = True


class Game:
    class States(IntEnum):
        register = 0
        all_turn = 1
        mafia_turn = 2
        finished = 3

    def __init__(self):
        self.state = Game.States.register
        self.players = {}
        self.current_targets = None
        self.current_voters = None
        self.current_votes = None

    def add_player(self, client, alias):
        if self.state != Game.States.register:
            return False
        index = len(self.players.keys())
        self.players[index] = Player(client, alias, index)
        client.send(MessageRegistered(index))
        for index in self.players.keys():
            self.players[index].client.send(MessagePlayers(self.players))
        return True

    def start(self):
        cards = []
        cards += [True for _ in range(MAFIA_COUNT)]
        cards += [False for _ in range(PLAYERS_FOR_READY - MAFIA_COUNT)]
        random.shuffle(cards)
        for i, player in enumerate(self.players.values()):
            player.mafia = cards[i]
            player.client.send(MessageReady(player.mafia))
        self.all_turn()

    # def on_ping(self, player):
    #     player.client.send(MessagePong())

    def on_chat(self, sender, msg):
        receivers = [player for player in self.players.values() if player.index != sender.index]
        for player in receivers:
            player.client.send(MessageChat(sender.index, msg))

    def on_vote(self, player, index):
        try:
            index = int(index)
            if not index in self.current_targets:
                raise
        except:
            player.client.send(MessageErr("Неверный индекс!"))
            return
        self.current_votes[player.index] = index
        player.client.send(MessageAccepted("accepted"))
        for voter in self.current_voters:
            voter.client.send(MessageVote(player.index, index))
        ready = True
        targets = {}
        for target in self.current_targets:
            targets[target] = 0
        for target in self.current_votes.values():
            if target == None:
                ready = False
                return
            targets[target] += 1
        if ready:
            to_kill = sorted(targets.keys(), key=functools.cmp_to_key(lambda a, b: -1 if targets[a] > targets[b] else 1 if targets[a] < targets[b] else 0))
            if len(to_kill) > 1 and targets[to_kill[0]] == targets[to_kill[1]]:
                for player in self.players.values():
                    player.client.send(MessageRevote())
                if self.state == Game.States.all_turn:
                    self.all_turn()
                elif self.state == Game.States.mafia_turn:
                    self.mafia_turn()
            else:
                target = self.players[to_kill[0]]
                target.alive = False
                for player in self.players.values():
                    player.client.send(MessageKill(target.index))
                citizens_cnt = len([player for player in self.players.values() if player.alive and not player.mafia])
                mafia_cnt = len([player for player in self.players.values() if player.alive and player.mafia])
                if citizens_cnt == 0:
                    self.end_game(True)
                elif mafia_cnt == 0:
                    self.end_game(False)
                elif citizens_cnt == 1 and mafia_cnt == 1:
                    self.end_game(True)
                else:
                    if self.state == Game.States.all_turn:
                        self.mafia_turn()
                    elif self.state == Game.States.mafia_turn:
                        self.all_turn()

    def change_state(self, state):
        self.state = state
        for player in self.players.values():
            player.client.send(MessageState(int(self.state)))

    def all_turn(self):
        self.change_state(Game.States.all_turn)
        self.current_targets = []
        self.current_voters = []
        self.current_votes = {}
        for player in self.players.values():
            if player.alive:
                self.current_targets += [player.index]
                self.current_voters += [player]
                self.current_votes[player.index] = None
        for player in self.current_voters:
            player.client.send(MessageTargets(self.current_targets))

    def mafia_turn(self):
        self.change_state(Game.States.mafia_turn)
        self.current_targets = []
        self.current_voters = []
        self.current_votes = {}
        for player in self.players.values():
            if player.alive:
                if player.mafia:
                    self.current_voters += [player]
                    self.current_votes[player.index] = None
                else:
                    self.current_targets += [player.index]
        for player in self.current_voters:
            player.client.send(MessageTargets(self.current_targets))

    def end_game(self, mafia):
        for player in self.players.values():
            player.client.send(MessageFinished(mafia))
        self.change_state(Game.States.finished)


class Server:
    def __init__(self, port):
        self.sock = socket.socket(socket.AF_INET)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind(("localhost", port))
        self.port = port
        self.clients = {}
        self.running = True
        self.game = Game()
        self.mutex = threading.Lock()

    def start(self):
        self.sock.listen(1)
        print("[ Server started at port %d ]" % self.port)
        while self.running:
            conn, addr = self.sock.accept()
            self.mutex.acquire()
            client = ClientOnServer(conn, addr)
            self.clients[client] = True
            threading.Thread(target=lambda: self.on_client(client)).start()
            self.mutex.release()

    def stop(self):
        self.mutex.acquire()
        self.running = False
        for client in self.clients.keys():
            print("Disconnecting %s" % client.to_string())
            client.conn.shutdown(socket.SHUT_RDWR)
            client.conn.close()
        self.sock.close()
        self.mutex.release()
        socket.socket(socket.AF_INET).connect(("localhost", self.port))

    def on_client(self, client):
        while True:
            try:
                msg_len = int.from_bytes(client.conn.recv(4), "big")
                msg = client.conn.recv(msg_len)
                self.on_message(client, json.loads(msg))
            except:
                self.mutex.acquire()
                print("Client %s disconnected" % client.to_string())
                self.clients.pop(client, None)
                self.mutex.release()
                break

    def on_message(self, client, msg):
        print("Received from '%s' %s" % (client.to_string(), json.dumps(msg)))
        command = msg["command"]
        args = msg["args"] if "args" in msg else None
        if command == "register":
            if not self.game.add_player(client, args["alias"]):
                client.send(MessageErr("Game already started"))
            if len(self.game.players) == PLAYERS_FOR_READY and self.game.state == Game.States.register:
                self.game.start()
        else:
            player = [player for player in self.game.players.values() if player.client == client]
            if len(player) != 0:
                player = player[0]
                # if command == "ping":
                    # self.game.on_ping(player)
                if command == "chat":
                    self.game.on_chat(player, args["msg"])
                elif command == "vote":
                    self.game.on_vote(player, args["index"])
        if self.game.state == Game.States.finished:
            self.stop()


if __name__ == '__main__':
    server = Server(1080)
    server.start()
