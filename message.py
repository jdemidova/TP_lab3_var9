import json


class MessageT:
    def __init__(self, command, args):
        self.command = command
        self.args = args

    def to_string(self):
        msg = {}
        if self.command:
            msg["command"] = self.command
        if self.args:
            msg["args"] = self.args
        return json.dumps(msg)
