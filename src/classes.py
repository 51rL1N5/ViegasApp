# Classe
# Frame
# ...

class Frame:
    def __init__(self, ip_dest, ip_orig, nickname, command, data):
        self.length   = len(data)
        self.ip_orig  = ip_orig
        self.ip_dest  = ip_dest
        self.nickname = nickname
        self.command  = command
        self.data     = data
        pass

class User:
    def __init__(self, nickname, addr):
        self.nickname = nickname
        self.addr     = addr
        pass
