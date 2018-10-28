from socket import *                       # sockets
from threading import Thread
from classes import Frame
from classes import Command as cmd

ip = '127.0.0.1'
port = 2626


class Client(Thread):
    def __ini__(self, name, ip, port):
        Thread.__init__(self)
        if nickNameValid(name) is False:
            raise Exception('NickName invalido')
            return
        if len(name) < 6: #para garantir que o nickName sempre ocuparar 6 octetos
            name = (6 - len(name))*' '
        self.name = name
        self.sock = socket(AF_INET,SOCK_STREAM)

        try:
            self.sock.connected(tuple(ip,port))
        except:
            print('Falha ao se conectar com o servidor')
            return

        self.finish= False

        self.ip_server  = ip
        self.port_server= port
        self.ip = socket.getsocketname()[0]

        self.buffer = list()
    def run(self):
        # Aguarda confirmacao de usuario criado...
        self.sock.send( Frame(self.ip,  self.ip_server, self.name, cmd.NEW, self.name)
        bitstream = self.sock.recv(LEN_MAX)
        frame = Frame(bitstream = bitstream)

        if frame.command is cmd.INVALID:
            raise Exception('Servidor rejeitou cadastrar novo usuario')

        while not finish:
            bitstream = self.sock.recv(LEN_MAX)
            frame = Frame(bitstream = bitstream)
            self.process(frame)

    def readLineEdit(self):

    def process(self, frame):

        if frame.command is cmd.LIST: #lista de conectados
            self.buffer += frame.data
        elif frame.command is cmd.LIST_SIZE: #numero de conectados
            pass
        elif frame.command is cmd.PUBLIC: #mensagem do chat public
            pass
        elif frame.command is cmd.PRIVATE: #mensagem do chat privado
            pass
        else:#ignorar demais comandos
            pass
    def nickNameValid(self, nickName):
        if len(nickName) > 6 or len(nickName) is '':
            return False
        return True

while True:
    nickName = input('Informe seu nick Name:\t')
    try:
        my_client = Client(NickName, ip, port)
        my_client.start()
        break
    except:
        pass

while True:
    msg = input('Digite:\t')
    frame = Frame('50.50.50.50', '40.40.40.40', nickName, 0, msg)
    client.send( pickle.dumps(frame))

    if not msg:break

client.close()
print('conexao encerrada')
