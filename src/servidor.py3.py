# UNIVERSIDADE FEDERAL DO RIO GRANDE DO NORTE
# DEPARTAMENTO DE ENGENHARIA DE COMPUTACAO E AUTOMACAO
# DISCIPLINA REDES DE COMPUTADORES (DCA0113)
# AUTOR: ...
#
# SCRIPT: ...

# importacao das bibliotecas
from socket import *                       # sockets
from threading import Thread
from classes import Frame
from classes import Command as cmd
from classes import Const as const
"""
 ----- Lista de comandos ----------
 0 -> mandar para todos
 1 -> pedido de lista de cleintes
 2 -> mudar de nome
 3 -> mandar mensagem privado
 4 -> sair
 5 -> Invalido
 6 -> OK
 7 -> Nova conexao
 8 -> Numero de conectados
"""
class Connected(Thread):
    def __init__(self,nickName, socket, addr):
        Thread.__init__(self)
        self.nickName = nickName
        self.socket   = socket
        self.addr     = addr
        self.ip       = addr[0]
        self.port     = addr[1]

        self.lastFrame = Frame()

        self.connected= True
        self.flag = False
        self.private= False

    def __str__(self):
        if self.private == True:
            return self.nickName + '(privado)'
        return self.nickName

    def run(self): #metodo para a thread
        while self.connected:
            # WARNING alterar limite para 56 bytes depois que estiver funcionando
            bitstream = self.socket.recv(const.LEN_MAX) # todo frame ocupa no maximo 56 bytes
            self.lastFrame = Frame(bitstream = bitstream)
            self.flag = True

            while self.flag: #aguarda o pedido ser tratado pelo server
                pass
        self.socket.close()

    def exit(self):
        self.connected = False
        self.socket.close()

    def send(self,frame): #dest eh outro Connected
        self.socket.send( bytes(frame) )

##########################################################################################
class Server(Thread):
    def __init__(self,port):
        Thread.__init__(self)
        # configura o servidor
        self.serverName = ''                            # ip do servidor (em branco)
        self.serverPort = port                          # porta a se conectar
        self.serverSocket = socket(AF_INET,SOCK_STREAM) # criacao do socket TCP
        self.serverSocket.bind((self.serverName,self.serverPort)) # bind do ip do servidor com a porta
        # inicia o servidor
        self.connecteds = []                            # vetor de client

        self.finish = False

    def run(self):
        # função para chamar a thread do bate papo
        print ('Servidor TCP esperando conexoes na porta %d ...' % (self.serverPort))

        self.serverSocket.settimeout(0.5)
        self.serverSocket.listen(1)                     # socket pronto para 'ouvir' conexoes

        while not self.finish:
          try:
              # print('Aguardando conexao')
              connectionSocket, addr = self.serverSocket.accept() # aceita as conexoes dos clientes
              print('Alguem se conectou...')
          except:
              # print('Verificando os conectados...')
              for user in self.connecteds:
                  if user.flag == True:
                      self.process(user)
              continue

          bitstream = connectionSocket.recv(const.LEN_MAX)
          if len(bitstream) < 16:
            connectionSocket.close()
            continue
          frame = Frame(bitstream = bitstream)
          if frame.command is not cmd.NEW:
              # pedido de nova conexao invalido
              connectionSocket.send( bytes(Frame(self.serverSocket.getsockname()[0], connectionSocket.getsockname()[0] , 'SERVER', cmd.INVALID, '')) )
              # print('Conexao rejeitada')
              continue

          # Cria um novo objeto connected e adiciona-o a lista de connecteds
          connected = Connected(frame.data, connectionSocket, addr)
          # confirmar para o client que ele foi adiciona ao servidor
          connected.send( bytes(Frame(self.serverSocket.getsockname()[0], connected.ip, 'SERVER', cmd.OK, '')))
          connected.start()

          self.connecteds.append(connected)
          welcome = str(connected.nickName) + 'acabou de entrar!'
          self.send_for_all(welcome)

        """
        A thread principal irá recepcionar o usuário novo
        Perguntará o seu nick.

        Em sequência, ela enviara uma Tupla contendo o ip do usuário + nickname
        """

    def process(self,user):
        # mandar mensagem para todos
        # connected = user #talvez seja necessario essa linha...
        if  user.lastFrame.command is cmd.PUBLIC:
            self.send_for_all(user.lastFrame.data, user)

        elif user.lastFrame.command is cmd.LIST: # pedir lista de clientes
            for other in self.connecteds:
                user.send( bytes(Frame(self.serverSocket.getsockname()[0], user.ip, 'SERVER', 1, str(other))))
            #para confirmar o final da lista
            user.send( bytes(Frame(self.serverSocket.getsockname()[0], user.ip, 'SERVER', 6, '')))
        elif user.lastFrame.command is cmd.CHANGE_NAME: #mudar de nome
            # falta verificar se nome ja esta em uso...
            newNick = user.lastFrame.data
            msg = 'Nick do '+ user.nickName + ' agora é ' + newNick
            user.nickName = newNick
            self.send_for_all(msg) #mensagem para todos
        elif user.lastFrame.command is cmd.PRIVATE:
            # dest = user.lastFrame.data
            print('Command 3- Ainda nao implementado')
        elif user.lastFrame.command is cmd.EXIT:
            msg = user.nickName + ' saiu!'
            self.send_for_all(msg)
            user.exit()
            user.join()
            self.connecteds.remove(user)
        # elif user.lastFrame.command == 5:
        #     print('Comando 5- Ainda nao implementado'
        else:
            #ignorar
            print('comando nao reconhecido')
        user.flag = False #pedido atendido

    def send_for_all(self,message, orig = None):
        # ENVIAR PRA GALERA
        for user in self.connecteds:
            if orig is not None:
                #mensagem de um conectado
                if  user.nickName is not orig.nickName:
                    user.send(bytes(Frame(orig.ip, user.ip, orig.nickName, cmd.PUBLIC, message)))
            else: #mensagem do servidor
                user.send( bytes((Frame('0.0.0.0', user.ip, 'SERVER', cmd.SERVER , message))) )
port = 3030
s = Server(port)
s.start()

while not s.finish:
    pass
s.join()
