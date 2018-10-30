# Classe
# Frame
# ...
class Command:
    PUBLIC      = 0
    LIST        = 1
    CHANGE_NAME = 2
    PRIVATE     = 3
    EXIT        = 4
    INVALID     = 5
    OK          = 6
    NEW         = 7
    LIST_SIZE   = 8 #numero de conectados
    LIST_END    = 9
    SERVER      = 200#mensagens do servidor, devem ser exibidas para todos os usuarios
    NONE        = 255

class Mode:
    PUBLIC  = 0  #MODO public
    PRIVATE = 1  #modo privado
class Const:
    LEN_MAX = 56 #tamanho maximo de um frame
    LEN_MIN = 16

class Frame:
    def __init__(self, ip_orig= '', ip_dest= '', nickname= '', command=-1, data= '', bitstream = None):

        self.length   = len(data)
        self.ip_orig  = ip_orig
        self.ip_dest  = ip_dest
        self.nickName = nickname
        self.command  = command
        self.data     = data

        if bitstream is not None:
            self.fromBitstream(bitstream)
    def bitStuff(self,nick):
        pass
    def buildBitstream(self):
        bitstream  = bytes(   [self.length]  )
        bitstream += bytes(   list( map(int, self.ip_orig.split('.')) )   )
        bitstream += bytes(   list( map(int, self.ip_dest.split('.')) )   )
        bitstream += bytes(self.nickName,  'utf-8')
        bitstream += bytes(   [self.command]  )
        bitstream += bytes(self.data, 'utf-8')
        return bitstream
    def __bytes__(self):
        return self.buildBitstream()
    def __len__(self):
        bitstream = self.buildBitstream()
        return len(bitstream)
    def makeIP_fromBitstream(self,ip_bitstream):
        ip_bits = ip_bitstream

        ip_tmp = str( list( map(int, ip_bits) ) ) # saida do tipo: '[192, 168, 0, 1]'
        ip_tmp = ip_tmp.replace(' ','') #remove espacos
        ip_tmp = ip_tmp.replace(',','.')
        ip_tmp = ip_tmp.replace('[','')
        ip_tmp = ip_tmp.replace(']','')
        #ao final teremos algo do tipo: '192.168.0.1'
        return ip_tmp
    def fromBitstream(self, bitstream):
        self.length  = int(bitstream[0])
        self.ip_orig = self.makeIP_fromBitstream(bitstream[1:5])
        self.ip_dest = self.makeIP_fromBitstream(bitstream[5:9])
        self.nickName= bitstream[9:15].decode('utf-8')
        self.command = int(bitstream[15])
        self.data    = bitstream[16:].decode('utf-8')

    def __str__(self):
        out = 'Length:\t'  + str(self.length)  + '\n'
        out+= 'IP orig:\t' + str(self.ip_orig) + '\n'
        out+= 'IP dest:\t' + str(self.ip_dest) + '\n'
        out+= 'NickName:\t'+ str(self.nickName)+ '\n'
        out+= 'Command:\t' + str(self.command) + '\n'
        out+= 'Data:\t'    + str(self.data)    + '\n'
        return out

# ip_orig = '192.168.0.1'
# ip_dest = '192.168.0.2'
# nick = 'Luis  '
# command = 30
# data = 'Hello Frame'
# f = Frame(ip_orig, ip_dest, nick, command, data)
# print(f)
# print(bytes(f))
# bitstream = bytes(f)
# print(Frame(bitstream = bitstream))
