from message import MessageT


class MessageRegistered(MessageT):
    def __init__(self, index):
        MessageT.__init__(self, "registered", {"index": index})


class MessagePlayers(MessageT):
    def __init__(self, players):
        MessageT.__init__(self, "players", {"players": [{"index": index,
                                                         "alias": players[index].alias}
                                                        for index in players.keys()]})


class MessageReady(MessageT):
    def __init__(self, mafia):
        MessageT.__init__(self, "ready", {"mafia": mafia})


class MessagePong(MessageT):
    def __init__(self):
        MessageT.__init__(self, "pong", None)


class MessageChat(MessageT):
    def __init__(self, msg):
        MessageT.__init__(self, "chat", {"msg": msg})


class MessageTargets(MessageT):
    def __init__(self, targets):
        MessageT.__init__(self, "targets", {"targets": targets})


class MessageVotes(MessageT):
    def __init__(self, votes):
        MessageT.__init__(self, "votes", {"votes": votes})


class MessageVote(MessageT):
    def __init__(self, player, target):
        MessageT.__init__(self, "vote", {"player": player, "target": target})


class MessageRevote(MessageT):
    def __init__(self):
        MessageT.__init__(self, "revote", None)


class MessageErr(MessageT):
    def __init__(self, msg):
        MessageT.__init__(self, "err", {"msg": msg})


class MessageKill(MessageT):
    def __init__(self, index):
        MessageT.__init__(self, "kill", {"index": index})


class MessageState(MessageT):
    def __init__(self, state):
        MessageT.__init__(self, "state", {"state": state})


class MessageFinished(MessageT):
    def __init__(self, mafia):
        MessageT.__init__(self, "finished", {"mafia": mafia})


class MessageAccepted(MessageT):
    def __init__(self, msg):
        MessageT.__init__(self, "accepted", {"accepted": msg})

