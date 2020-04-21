from message import MessageT


class MessageRegisterOnClient(MessageT):
    def __init__(self, alias):
        MessageT.__init__(self, "register", {"alias": alias})


# class MessagePingOnClient(MessageT):
#     def __init__(self):
#         MessageT.__init__(self, "ping", None)


class MessageVoteOnClient(MessageT):
    def __init__(self, target):
        MessageT.__init__(self, "vote", {"index": target})


class MessageChatOnClient(MessageT):
    def __init(self, msg):
        MessageT.__init__(self, "chat", {"msg": msg})
