# UNIVERSIDADE FEDERAL DO RIO GRANDE DO NORTE
# DEPARTAMENTO DE ENGENHARIA DE COMPUTACAO E AUTOMACAO
# DISCIPLINA REDES DE COMPUTADORES (DCA0113)
# AUTOR: ...
#
# SCRIPT: ...

# importacao das bibliotecas
from socket import *                       # sockets
from threading import Thread
from classes import *
import pickle
"""
 ----- Lista de comandos ----------
 0 -> mandar para todos
 1 -> pedido de lista de cleintes
 2 -> mudar de nome
 3 -> mandar mensagem privado
 4 -> sair
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
            recv = self.socket.recv(1024) # todo frame ocupa no maximo 56 bytes
            frame = pickle.loads(recv)
            self.flag = True
            print(self.nickName, ' diz:\t', frame.data)

            while self.flag: #aguarda o pedido ser tratado pelo server
                pass

        self.socket.close()

    def exit(self):
        self.connected = False
        self.flag = False
        self.socket.close()

    def send(self,msg, dest): #dest eh outro Connected
        frame = Frame(dest.ip, self.ip, self.nickName, 0, msg)
        # self.socket.sendto(pickle.dumps(frame), dest.addr)
        self.socket.send(pickle.dumps(frame))
        # pass
# #########################################################################################

port = 2626

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

    def handle(self,user):

        # mandar mensagem para todos
        if  user.lastFrame.command == 0:
            self.send_for_all(user.lastFrame.data, user.nickName)

        elif user.lastFrame.command == 1: # pedir lista de clientes
            self.send_for_all('------- Lista de gente ---------\n', '')
            for connected in self.connecteds:
                self.send_for_all('', connected.nickName)
            self.send_for_all('--------------------------------', '')
        elif user.lastFrame.command == 2: #mudar de nome
            newNick = user.lastFrame.data
            msg = 'Nick do '+ user.nickName + ' agora é ' + newNick
            user.nickName = newNick
            self.send_for_all(msg , '') #mensagem para todos
        elif user.lastFrame.command == 3:
            # dest = user.lastFrame.data
            print('Comando 3- Ainda nao implementado')
            pass
        elif user.lastFrame.command == 4:
            msg = user.nickName + ' saiu!'
            user.exit()
            user.join()

            self.send_for_all(msg , '')
        elif user.lastFrame.command == 5:
            print('Comando 5- Ainda nao implementado')
        user.flag = False #pedido atendido


    def run(self):
        # função para chamar a thread do bate papo
        print ('Servidor TCP esperando conexoes na porta %d ...' % (self.serverPort))

        self.serverSocket.settimeout(0.5)
        self.serverSocket.listen(1)                     # socket pronto para 'ouvir' conexoes

        while not self.finish:
          try:
              connectionSocket, addr = self.serverSocket.accept() # aceita as conexoes dos clientes
          except:
              for user in self.connecteds:
                  if user.flag == True:
                      self.handle(user)
              continue

          nickname = connectionSocket.recv(1024)
          nickname = nickname.decode('utf-8')
          print(nickname, '  Acabou de entrar!!')

          if len(nickname) == 0:
              connectionSocket.close()
              continue

          connected = Connected(nickname, connectionSocket, addr)

          connected.start()

          self.connecteds.append(connected)
          welcome = str(nickname) + '\nacabou de entrar\n'
          self.send_for_all(welcome, '')

        """
        A thread principal irá recepcionar o usuário novo
        Perguntará o seu nick.

        Em sequência, ela enviara uma Tupla contendo o ip do usuário + nickname
        """
        # pass

    def send_for_all(self,message, orig):
        # ENVIAR PRA GALERA KKKKKKK
        # try:
        for user in self.connecteds:
            if user.nickName != orig:
                user.send(message, user)
        # except:
        #     print ('EROU')
        # pass
s = Server(port)
s.start()

while not s.finish:
    pass
s.join()
