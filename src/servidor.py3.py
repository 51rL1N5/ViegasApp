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
# from classes import MySocket
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
        # self.addr     = addr
        self.nickName = nickName
        self.socket   = socket
        self.socket.settimeout(10)
        self.ip       = addr[0]
        self.port     = addr[1]

        self.lastFrame = Frame()

        self.connected= True
        self.flag = False
        self.private= False

    def __str__(self):
        name = ''
        if self.private == True:
            name = self.nickName + '(privado)'
        name = self.nickName
        return name + ', ' +str(self.ip) + ', ' + str(self.port)

    def run(self): #metodo para a thread
        while self.connected:
            try:
                bitstream = self.socket.recv(const.LEN_MAX) # todo frame ocupa no maximo 56 bytes
                self.lastFrame = Frame(bitstream = bitstream)
                self.flag = True
            except:
                continue

            while self.flag: #aguarda o pedido ser tratado pelo server
                pass
        self.socket.close()

    def exit(self):
        self.connected = False
        self.flag = False
        self.socket.close()

    def sendFrame(self,frame): #dest eh outro Connected
        try:
            self.socket.send( bytes(frame) )
        except:
            self.socket.close()
            self.exit()
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

        """
        A thread principal irá recepcionar o usuário novo
        Perguntará o seu nick.

        Caso nao haja novos pedidos de conexao, o servidor ira tratar dos pedidos
        feitos pelos usuarios conectados.
        """
        while not self.finish:
          try:
              connectionSocket, addr = self.serverSocket.accept() # aceita as conexoes dos clientes
          except:
              for user in self.connecteds:
                  if user.flag == True:
                      try:
                          self.process(user)
                      except Exception as erro: #caso de algum erro na comunicacao, remover da lista e garantir que foi fechado
                          self.connecteds.remove(user)
                          user.exit()
                          user.join()
              continue

          try:
              bitstream = connectionSocket.recv(const.LEN_MAX)
          except:
              continue
          if len(bitstream) < const.LEN_MIN:
            connectionSocket.close()
            continue
          frame = Frame(bitstream = bitstream)
          if frame.command is not cmd.NEW:
              # pedido de nova conexao invalido
              try:
                  connectionSocket.send( bytes(Frame(self.serverSocket.getsockname()[0], connectionSocket.getsockname()[0] , 'SERVER', cmd.INVALID, '')) )
              except Exception as erro:
                  connectionSocket.close()
              continue

          # Cria um novo objeto connected e adiciona-o a lista de connecteds
          connected = Connected(frame.data, connectionSocket, addr)
          # confirmar para o client que ele foi adiciona ao servidor
          try:
              connected.sendFrame( bytes(Frame(self.serverSocket.getsockname()[0], connected.ip, 'SERVER', cmd.OK, '')))
          except Exception as erro:
              continue
          connected.start()

          self.connecteds.append(connected)
          welcome = str(connected.nickName) + '\tacabou de entrar!'
          # print(welcome)
          self.send_for_all(welcome)

    def process(self,user):
        # mandar mensagem para todos

        if  user.lastFrame.command is cmd.PUBLIC:
            self.send_for_all(user.lastFrame.data, user)
        elif user.lastFrame.command == cmd.LIST: # pedir lista de clientes
            for other in self.connecteds:
                try:
                    user.sendFrame( Frame(self.serverSocket.getsockname()[0], user.ip, 'SERVER', cmd.LIST, str(other)))
                except:
                    user.join()
                    user.exit()
                    self.connecteds.remove(user)
            user.sendFrame( Frame(self.serverSocket.getsockname()[0], user.ip, 'SERVER', cmd.LIST_END, str(other)))
            #para confirmar o final da lista
            try:
                user.sendFrame( Frame(self.serverSocket.getsockname()[0], user.ip, 'SERVER', 6, ''))
            except:
                user.exit()
                user.join()
                self.connecteds.remove(user)
        elif user.lastFrame.command is cmd.NAME: #mudar de nome
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
        elif user.lastFrame.command is cmd.SHUTDOWN:
            if user.nickName == 'Sadmin':
                self.exit()
        else:
            #ignorar
            print('comando nao reconhecido')
        user.flag = False #pedido atendido
    def send_for_all(self,message, orig = None):
        # ENVIAR PRA GALERA
        for user in self.connecteds:
            if orig is not None:
                #mensagem de um conectado
                print('< %s > %s' %(orig, message))

                if  user.nickName is not orig.nickName:
                    try:
                        user.sendFrame(bytes(Frame(orig.ip, user.ip, orig.nickName, cmd.PUBLIC, message)))
                    except:
                        user.exit()
                        usr.join()
                        self.connecteds.remove(user)
            else: #mensagem do servidor
                try:
                    user.sendFrame( bytes((Frame('0.0.0.0', user.ip, 'SERVER', cmd.SERVER , message))) )
                    print(message)
                except:
                    user.exit()
                    user.join()
                    self.connecteds.remove(user)
    def exit(self):
        self.send_for_all('SERVIDOR ESTA SENDO DESLIGADO!')
        self.finish = True
        for user in self.connecteds:
            user.exit()
            user.join()
            try:
                self.connecteds.remove(user)
            except:
                pass
        self.finish = True

    def identify_command(self,string):
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

        # busca por list()
        if func == 'list':
            print('____________Lista de Conectados____________')
            for user in self.connecteds:
                print(user)
            print('____________Fim da Lista____________')
        # busca por exit()
        elif func == 'exit':
            self.exit()
        # busca por help()
        elif func == 'help':
            self.help()
        else:#ignorar
            pass
    def help(self):
        print(5*'_'+'Comandos do servidor'+ 5*'_')
        print('help()')
        print('exit()')
        print('list()')
        print(10*'_'+ len('Comandos do servidor')*'_')

    def readLine(self):
        line = input()
        self.identify_command(line)

port = 3030
s = Server(port)
s.start()
s.help()

while not s.finish:
    s.readLine()
    pass
print('Servidor finalizado com sucesso!')
s.join()
