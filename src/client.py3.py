from socket import *                       # sockets
from threading import Thread
from classes import Frame
from classes import Command as cmd
from classes import Mode


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
        self.ip = sock.getsocketname()[0]

        self.buffer = list()
        self.buffer_ready = False

        self.mode = Mode.PUBLIC
        self.dest_private = '' #nick do usuario com quem este esta em privado
    def run(self):
        # Aguarda confirmacao de usuario criado...
        self.sock.send( Frame(self.ip,  self.ip_server, self.name, cmd.NEW, self.name) )
        frame = self.readFrame()

        if frame.command is cmd.INVALID:
            raise Exception('Servidor rejeitou cadastrar novo usuario')

        while not finish:
            frame = self.readFrame()
            self.process(frame)

    def readFrame(self):
        bitstream = self.sock.recv(LEN_MAX)
        return Frame(bitstream = bitstream)
    def send_public(self, msg):
        pass
    def send_private(self, msg):
        pass
    def changeName(self,newName):
        pass
    def help(self):
        print(10*'_'+'LISTA_DE_COMANDOS_DO_CLIENTE'+10*'_')
        print('private(dest)')
        print('public()')
        print('exit()')
        print('chage_name(NewName)')
        print('list_size()')
        print('help()')

    def identify_ommand(self,string):
        r = cmd.PUBLIC
        string_tmp = string
        # verifica se pode ser uma funcao
        if string_tmp.find('(') is -1: #apenas uma mensagem
            return (r,string)
        if string_tmp.find(')') is -1:
            return (r,string)
        func = string_tmp[0: string_tmp.find('(')]
        arg  = string_tmp[string_tmp.find('(')-1: string_tmp.find(')')]

        # para uma entrada no formato: 'func(arg)'

        # busca por private(...)
        if func is 'private':
            print('Comando ainda nao implementado')
        # busca por list()
        elif func is 'list':
            self.requestList()
        # busca por exit()
        elif func is 'exit':
            r = cmd.EXIT
        # busca por list_size()
        elif func is 'list_size':
            r = cmd.LIST_SIZE
        # busca por change_name(...)
        elif func is 'change_name':
            print('Comando ainda nao implementado')
        # busca por help()
        elif func is 'help':
            self.help();
            return (cmd.NONE, '')
        else:#ignorar
            pass
        return (r,arg)

    def readLineEdit(self, line): #identifica as palavras chaves na linha lida no temrinal e encaminha para o servidor
        command, arg = identify_ommand(line)
        if command is cmd.PUBLIC:
            self.sock.send( Frame(self.ip, self.ip_server, self.name, cmd.PUBLIC, arg) )
        elif command is cmd.EXIT:
            self.sock.send( Frame(self.ip, self.ip_server, self.name, cmd.EXIT, arg) )
            self.exit()
        else:#ignorar
            pass


    def exit(self):
        self.sock.close()
        self.finish = True
        self.buffer.clear()

    def requestList(self):
        self.buffer.clear()

        while not self.buffer_ready: #aguarda pelo final da lista
            pass

        print('____________Lista de Conectados____________')
        for user in self.buffer:
            print(user)
        self.buffer_ready = False

    def process(self, frame):
        command = frame.command
        data = frame.data
        orig = frame.nickName
        dest = frame.ip_dest

        if dest is not self.ip:
            print('Recebi uma mensagem que nao era para mim ? ...')
            return

        if command is cmd.LIST: #lista de conectados
            self.buffer.append(data)
        elif command is cmd.LIST_SIZE:
            print('\n****Numero de conectados no momento***:\t', data)
        elif command is cmd.PUBLIC: #mensagem do chat public
            print(orig, '  Diz:\t', data)
        elif command is cmd.PRIVATE: #mensagem do chat privado
            print(orig, '(private) Diz:\t', data)
        elif command is cmd.LIST_END: #servidor mandou toda a lista de usuarios conectados
            self.buffer_ready = True
        elif command is cmd.SERVER:
            print(5*'*' + 'MENSAGEM DO SERVIDOR' + 5*'*:\t', data)
        else:#ignorar demais comandos
            pass

    def nickNameValid(self, nickName):
        if len(nickName) > 6 or len(nickName) is '':
            return False
        return True


ip = '127.0.0.1'
port = 2626

while True:
    nickName = input('Informe seu nick Name:\t')
    try:
        my_client = Client(NickName, ip, port)
        my_client.start() #lanca thread
        break
    except Exception as error:
        print('Erro:\t',error)
        continue

while my_client.finish is False:
    msg = input('Digite:\t')
    my_client.readLineEdit(msg)

my_client.join() #aguarda para terminar a thread
print('conexao encerrada')
