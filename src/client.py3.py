from socket import *                       # sockets
from threading import Thread
from classes import Frame
from classes import Command as cmd
from classes import Mode
from classes import Const as const

class Client(Thread):
    def __init__(self, name, ip, port):
        Thread.__init__(self)
        if self.nickNameValid(name) is False:
            raise Exception('NickName invalido')
            return
        if len(name) < 6: #para garantir que o nickName sempre ocuparar 6 octetos
            name += (6 - len(name))*' '
        self.name = name
        self.sock = socket(AF_INET,SOCK_STREAM)
        # self.sock.settimeout(30)
        # try:
        # except Exception as erro:
            # Exception(erro)
            # print('Falha ao se conectar com o servidor')
        self.finish= False

        self.ip_server  = ip
        self.port_server= port
        self.ip = self.sock.getsockname()[0]
        # s.getsockname
        self.buffer = list()
        self.buffer_ready = False

        self.mode = Mode.PUBLIC
        self.dest_private = '' #nick do usuario com quem este esta em privado
    def run(self):
        self.sock.connect( (self.ip,self.port_server) )
        self.sendFrame( Frame(self.ip,  self.ip_server, self.name, cmd.NEW, self.name) )
        # recebe respota do servidor
        frame_rec = self.recvFrame()

        if frame_rec.command == cmd.INVALID:
            raise Exception('Servidor rejeitou cadastrar novo usuario')
        print('Conectado com o servidor!')

        while not self.finish:
            frame_rec = self.recvFrame()
            self.process(frame_rec)

    def sendFrame(self, frame):
        try:
            self.sock.send(bytes(frame))
        except:
            print('FALHA NA COMUNICAÇÃO COM SERVIDOR!!')
            self.exit()
            return

    def recvFrame(self):
        try:
            bitstream = self.sock.recv(const.LEN_MAX)
        except:
            print("FALHA NA COMUNICAÇÃO COM O Servidor!!")
            self.exit()
            exit()
        if len(bitstream) < const.LEN_MIN:
            return Frame()
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

    def identify_command(self,string):
        # print('identify_command:',string)

        r = cmd.PUBLIC
        # verifica se pode ser uma funcao
        if string.find('(') is -1: #apenas uma mensagem
            return (r,string)
        if string.find(')') is -1:
            return (r,string)

        l_string = string.split('(')
        func = l_string[0]
        arg  = l_string[1].replace(')','')

        func.replace(' ','')
        arg.replace(' ','')
        func = func.lower()
        arg = arg.lower()

        # busca por private(...)
        if func == 'private':
            print('Comando ainda nao implementado')
        # busca por list()
        elif func == 'list':
            print('request List, em andamento...')
            self.requestList()
        # busca por exit()
        elif func == 'exit':
            print('exit, em andamento...')
            r = cmd.EXIT
        # busca por list_size()
        elif func == 'list_size':
            print('request List_Size, em andamento...')
            r = cmd.LIST_SIZE
        # busca por change_name(...)
        elif func == 'change_name':
            print('Comando ainda nao implementado')
        # busca por help()
        elif func == 'help':
            self.help();
            return (cmd.NONE, '')
        else:#ignorar
            print('comando ignorado')
            pass
        return (r,arg)

    def readLineEdit(self, line): #identifica as palavras chaves na linha lida no temrinal e encaminha para o servidor
        command, arg = self.identify_command(line)
        if command is cmd.PUBLIC:
            self.sendFrame
            self.sendFrame( Frame(self.ip, self.ip_server, self.name, cmd.PUBLIC, arg) )
        elif command is cmd.EXIT:
            print('Finalizando o cliente...')
            self.sendFrame( Frame(self.ip, self.ip_server, self.name, cmd.EXIT, arg) )
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

        # if dest is not self.ip:
        #     print('Recebi uma mensagem que nao era para mim ? ...')
        #     return

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
            print(5*'*' + 'MENSAGEM DO SERVIDOR' + 5*'*' + ':\t', data)
        else:#ignorar demais comandos
            pass
    def connected(self):
        return bool(not self.finish)
    def nickNameValid(self, nickName):
        if len(nickName) > 6 or len(nickName) is '':
            return False
        return True


ip = '127.0.0.1'
port = 3030

# while True:
nickName = input('Informe seu nick Name:\t')
    # try:
my_client = Client(nickName, ip, port)
my_client.start() #lanca thread
        # break
    # except Exception as error:
    #     print('Erro:\t',error)
    #     continue

while my_client.connected():
    msg = input('Digite:\t')
    my_client.readLineEdit(msg)
    pass

my_client.exit()
my_client.join() #aguarda para terminar a thread
print('conexao encerrada')
