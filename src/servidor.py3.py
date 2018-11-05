# UNIVERSIDADE FEDERAL DO RIO GRANDE DO NORTE
# DEPARTAMENTO DE ENGENHARIA DE COMPUTACAO E AUTOMACAO
# DISCIPLINA REDES DE COMPUTADORES (DCA0113)
# AUTOR: ...
#
# SCRIPT: ...

# importacao das bibliotecas
from socket import *                       # sockets
from threading import Thread
from classes import Frame, Mode
from classes import Command as cmd
from classes import Const as const

import time
import os
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
        self.socket.settimeout(5)
        self.ip       = addr[0]
        self.port     = addr[1]

        self.lastFrame = Frame()

        self.connected= True
        self.flag     = False #para interrupcao paralela

    def __str__(self):
        name = self.nickName
        return name + ', ' +str(self.ip) + ', ' + str(self.port)

    def run(self): #metodo para a thread
        time_max = 10
        while self.connected:
            time_count= 0
            try:
                bitstream = self.socket.recv(const.LEN_MAX) # todo frame ocupa no maximo 56 bytes
                self.lastFrame = Frame(bitstream = bitstream)
                self.flag = True
            except:
                continue

            while (self.flag == True) and (time_count < time_max): #aguarda o pedido ser tratado pelo server
                time.sleep(0.05)
                time_count+=1
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
        while self.finish == False:
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
                    user.sendFrame( Frame(self.serverSocket.getsockname()[0], user.ip, 'SERVER', cmd.LIST_END, str(other)))
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
            # busca o usuario cujo nick seja: user.lastFrame.nickname
            dest = user.lastFrame.data.split(',')[0]
            msg  = user.lastFrame.data[len(dest)+1:]

            for other_user in self.connecteds:
                if dest == other_user.nickName:
                    other_user.sendFrame( Frame(user.ip, other_user.ip, user.nickName, cmd.PRIVATE, msg) )
            # envia a mensagem diretamente para ele

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
            pass
        user.flag = False #pedido atendido
    def send_for_all(self,message, orig = None):
        # ENVIAR PRA GALERA
        if orig is not None:
            print('< %s > %s' %(orig, message))
        else:
            print(message)
        for user in self.connecteds:
            if orig is not None:
                #mensagem de um conectado
                if  user.nickName != orig.nickName:
                    try:
                        user.sendFrame(Frame(orig.ip, user.ip, orig.nickName, cmd.PUBLIC, message))
                    except:
                        user.exit()
                        usr.join()
                        self.connecteds.remove(user)
            else: #mensagem do servidor
                try:
                    user.sendFrame( (Frame('0.0.0.0', user.ip, 'SERVER', cmd.SERVER , message)) )
                except:
                    user.exit()
                    user.join()
                    self.connecteds.remove(user)
    def exit(self):
        self.send_for_all('SERVIDOR ESTA SENDO DESLIGADO!')
        for user in self.connecteds:
            try:
                user.sendFrame( (Frame('0.0.0.0', user.ip, 'SERVER', cmd.EXIT , '')) )
                user.exit()
                user.join()
            except:
                pass
        self.finish = True

    def identify_command(self,string):
        # verifica se pode ser uma funcao
        if string.find('(') is -1: #apenas uma mensagem
            return
        if string.find(')') is -1:
            return

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
        elif func == 'clear':
            os.system('clear')
            self.help()
        else:#ignorar
            pass
    def help(self):
        print(5*'_'+'Comandos do servidor'+ 5*'_')
        print('help()')
        print('exit()')
        print('list()')
        print('clear()')
        print(10*'_'+ len('Comandos do servidor')*'_')
    def readLine(self):
        line = input()
        self.identify_command(line)

port = 3131
s = Server(port)
s.start()
s.help()

while not s.finish:
    s.readLine()
    pass
print('Servidor finalizado com sucesso!')
s.join()
