
from PyQt5 import QtCore, QtGui, QtWidgets
from threading import Thread
from socket import *
import sys
import time

from classes import Frame
from classes import Command as cmd
from classes import Mode
from classes import Const as const

class Ui_Chat_Client(Thread):

    def __init__(self, name, ip, port):
        Thread.__init__(self)

        if self.nickNameValid(name) is False:
            raise Exception('NickName invalido')
            return
        if len(name) < 6: #para garantir que o nickName sempre ocuparar 6 octetos
            name += (6 - len(name))*' '
        self.name = name
        try:
            self.sock = socket(AF_INET,SOCK_STREAM)
        except:
            print('Falha ao estabelecer uma conexao com o servidor')
            self.exit()
            return

        self.finish= False

        self.ip_server  = ip
        self.port_server= port
        self.ip = self.sock.getsockname()[0]

        self.buffer = list()
        self.buffer_ready = False

        self.mode = Mode.PUBLIC
        self.dest_private = '' #nick do usuario com quem este esta em privado
    def run(self):
        self.sock.connect( (self.ip,self.port_server) )
        self.sendFrame( Frame(self.ip,  self.ip_server, self.name, cmd.NEW, self.name) )
        # recebe respota do servidor
        frame_rec = self.recvFrame()
        if frame_rec.command is cmd.INVALID:
            print('Servidor rejeitou cadastrar novo usuario')
            raise Exception('Servidor rejeitou cadastrar novo usuario')
        print('Conectado com o servidor!')

        while self.finish is False:
            frame_rec = self.recvFrame()
            self.process(frame_rec)

    def sendFrame(self, frame):
        try:
            self.sock.send(bytes(frame))
        except:
            print('Falha na comunicacao com o servidor!')
            self.finish = True
            self.sock.close()
            return
    def recvFrame(self):
        try:
            bitstream = self.sock.recv(const.LEN_MAX)
        except:
            if self.finish is not True:
                print("FALHA NA COMUNICAÇÃO COM O Servidor!!")
                self.exit()
            # exit()
            return Frame()
        if len(bitstream) < const.LEN_MIN:
            return Frame()
        return Frame(bitstream = bitstream)

    def help(self):
        self.listMsg.addItem(5*'_'+'LISTA_DE_COMANDOS_DO_CLIENTE'+5*'_')
        self.listMsg.addItem('private(dest,msg)')
        self.listMsg.addItem('public()')
        self.listMsg.addItem('exit()')
        self.listMsg.addItem('change_name()')
        self.listMsg.addItem('list()')
        self.listMsg.addItem('help()')
        self.listMsg.addItem('name(newName)')
        self.listMsg.addItem('clear()')

    def identify_command(self,string):
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

        # busca por private(...)
        if func == 'private':
            r = cmd.PRIVATE
            dest = arg.split(',')[0]
            msg  = arg[len(dest)+1:]
            if len(dest) < 6:
                dest += ( 6 - len(dest))*' '
            arg = dest + ',' +msg
        # busca por list()
        elif func == 'clear':
            self.listMsg.clear()
            r = cmd.NULL
        elif func == 'list':
            r = cmd.LIST
            self.listWidget.clear()
        # busca por exit()
        elif func == 'exit':
            r = cmd.EXIT
        # busca por change_name(...)
        elif func == 'name':
            # self.listMsg.addItem('Comando ainda nao implementado')
            if self.nickNameValid(arg) is True:
                r = cmd.NAME
                self.label_myName.setText(arg)

        # busca por help()
        elif func == 'help':
            self.help();
            # return (cmd.NULL, '')
            r = cmd.NULL
        elif func == 'shutdown':
            return (cmd.SHUTDOWN, '')
        else:#ignorar
            pass
        return (r,arg)
    def readLineEdit(self): #identifica as palavras chaves na linha lida no temrinal e encaminha para o servidor
        line = self.lineEdit.text()
        command, arg = self.identify_command(line)
        self.lineEdit.clear()

        if command is cmd.NULL:
            return

        self.sendFrame( Frame(self.ip, self.ip_server, self.name, command, arg) )
        if command is cmd.EXIT:
            print('Finalizando o cliente...')
            try:
                # self.sendFrame( Frame(self.ip, self.ip_server, self.name, cmd.EXIT, arg) )
                self.exit()
            except:
                self.finish = True
                exit()
        if command is cmd.LIST:
            self.requestList()

        self.listMsg.addItem('< você > %s' %line)

    def exit(self):
        try:
            self.sendFrame( Frame(self.ip, self.ip_server, self.name, cmd.EXIT, arg) )
        except:
            pass
        self.sock.close()
        self.finish = True
        self.buffer.clear()

    def requestList(self):
        self.buffer.clear()
        time_max = 10
        time_count= 0

        while (self.buffer_ready == False) and (time_count <= time_max): #aguarda pelo final da lista
            time.sleep(0.1)
            time_count += 1

        self.listMsg.addItem('____________Lista de Conectados____________')
        for user in self.buffer:
            self.listWidget.addItem(user)
            self.listMsg.addItem(user)
        self.listMsg.addItem('____________Fim da Lista____________')
        self.buffer_ready = False

    def process(self, frame):
        command = frame.command
        data = frame.data
        orig = frame.nickName
        dest = frame.ip_dest

        if command is cmd.LIST: #lista de conectados
            self.buffer.append(data)
        elif command is cmd.PUBLIC: #mensagem do chat public
            self.listMsg.addItem('< %s > %s' %(orig, data))
        elif command is cmd.PRIVATE: #mensagem do chat privado
            self.listMsg.addItem('< %s >(PRIVATE) %s' %(orig, data))
        elif command is cmd.LIST_END: #servidor mandou toda a lista de usuarios conectados
            self.buffer_ready = True
        elif command is cmd.SERVER:
            self.listMsg.addItem('{ %s } %s' %('SERVIDOR', data))
        elif command is cmd.EXIT:
            self.exit()
        else:#ignorar demais comandos
            pass
    def connected(self):
        return bool(not self.finish)
    def nickNameValid(self, nickName):
        if len(nickName) > 6 or len(nickName) is '':
            return False
        return True

    def setupUi(self, Chat_Client):
        Chat_Client.setObjectName("Chat_Client")
        Chat_Client.resize(366, 294)
        Chat_Client.setMaximumSize(QtCore.QSize(366, 294))

        self.pushButton_help = QtWidgets.QPushButton(Chat_Client)
        self.pushButton_help.setGeometry(QtCore.QRect(290, 10, 51, 21))
        self.pushButton_help.setObjectName("pushButton_help")
        self.pushButton_help.setAutoDefault(False)
        self.widget = QtWidgets.QWidget(Chat_Client)
        self.widget.setGeometry(QtCore.QRect(0, 0, 260, 279))
        self.widget.setObjectName("widget")
        self.verticalLayout_4 = QtWidgets.QVBoxLayout(self.widget)
        self.verticalLayout_4.setContentsMargins(11, 11, 11, 11)
        self.verticalLayout_4.setSpacing(6)
        self.verticalLayout_4.setObjectName("verticalLayout_4")
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_2.setSpacing(6)
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.verticalLayout_3 = QtWidgets.QVBoxLayout()
        self.verticalLayout_3.setSpacing(6)
        self.verticalLayout_3.setObjectName("verticalLayout_3")
        self.label_Name = QtWidgets.QLabel(self.widget)
        self.label_Name.setObjectName("label_Name")
        self.verticalLayout_3.addWidget(self.label_Name)
        self.label_Mode = QtWidgets.QLabel(self.widget)
        self.label_Mode.setObjectName("label_Mode")
        self.verticalLayout_3.addWidget(self.label_Mode)
        self.horizontalLayout_2.addLayout(self.verticalLayout_3)
        self.verticalLayout_2 = QtWidgets.QVBoxLayout()
        self.verticalLayout_2.setSpacing(6)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.label_myName = QtWidgets.QLabel(self.widget)
        self.label_myName.setObjectName("label_myName")
        self.verticalLayout_2.addWidget(self.label_myName)
        self.label_myMode = QtWidgets.QLabel(self.widget)
        self.label_myMode.setObjectName("label_myMode")
        self.verticalLayout_2.addWidget(self.label_myMode)
        self.horizontalLayout_2.addLayout(self.verticalLayout_2)
        self.verticalLayout_4.addLayout(self.horizontalLayout_2)
        self.verticalLayout = QtWidgets.QVBoxLayout()
        self.verticalLayout.setSpacing(6)
        self.verticalLayout.setObjectName("verticalLayout")
        self.listMsg = QtWidgets.QListWidget(self.widget)
        self.listMsg.setObjectName("listMsg")
        self.verticalLayout.addWidget(self.listMsg)
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setSpacing(6)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.label_message = QtWidgets.QLabel(self.widget)
        self.label_message.setObjectName("label_message")
        self.horizontalLayout.addWidget(self.label_message)
        self.lineEdit = QtWidgets.QLineEdit(self.widget)
        self.lineEdit.setFrame(True)
        self.lineEdit.setCursorMoveStyle(QtCore.Qt.LogicalMoveStyle)
        self.lineEdit.setObjectName("lineEdit")
        self.horizontalLayout.addWidget(self.lineEdit)
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.verticalLayout_4.addLayout(self.verticalLayout)
        self.widget1 = QtWidgets.QWidget(Chat_Client)
        self.widget1.setGeometry(QtCore.QRect(270, 40, 91, 241))
        self.widget1.setObjectName("widget1")
        self.verticalLayout_5 = QtWidgets.QVBoxLayout(self.widget1)
        self.verticalLayout_5.setContentsMargins(11, 11, 11, 11)
        self.verticalLayout_5.setSpacing(6)
        self.verticalLayout_5.setObjectName("verticalLayout_5")
        self.label = QtWidgets.QLabel(self.widget1)
        self.label.setObjectName("label")
        self.verticalLayout_5.addWidget(self.label)
        self.listWidget = QtWidgets.QListWidget(self.widget1)
        self.listWidget.setObjectName("listWidget")
        self.verticalLayout_5.addWidget(self.listWidget)

        self.retranslateUi(Chat_Client)
        QtCore.QMetaObject.connectSlotsByName(Chat_Client)

        self.label_myMode.setText('PUBLIC')
        self.label_myName.setText(self.name)

        self.pushButton_help.clicked.connect(self.help)
        self.lineEdit.returnPressed.connect(self.readLineEdit)
        Chat_Client.finished.connect(self.exit)

    def retranslateUi(self, Chat_Client):
        _translate = QtCore.QCoreApplication.translate
        Chat_Client.setWindowTitle(_translate("Chat_Client", "Chat_Client"))
        self.pushButton_help.setText(_translate("Chat_Client", "HELP"))
        self.label_Name.setText(_translate("Chat_Client", "Name"))
        self.label_Mode.setText(_translate("Chat_Client", "Mode"))
        self.label_myName.setText(_translate("Chat_Client", "ERRO"))
        self.label_myMode.setText(_translate("Chat_Client", "ERRO"))
        self.label_message.setText(_translate("Chat_Client", "Mensagem:"))
        self.label.setText(_translate("Chat_Client", "Conectados"))

if __name__ == "__main__":
    import sys

    ip = '127.0.0.1'
    port = 3131
    nickName = input('Informe seu nick Name(de até 6 caracteres!):\t')

    app = QtWidgets.QApplication(sys.argv)
    Chat_Client = QtWidgets.QDialog()
    ui = Ui_Chat_Client(nickName, ip, port)

    ui.setupUi(Chat_Client)
    ui.start()
    Chat_Client.show()
    sys.exit(app.exec_())
    print('end...')
    ui.join()
