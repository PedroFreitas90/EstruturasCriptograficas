from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes, hmac
from cryptography.exceptions import InvalidSignature
import getpass
import socket
import os

#Key Derivation Function
def passKDF(salt):
    kdf = PBKDF2HMAC(
        algorithm = hashes.SHA256(),
        length = 32,
        salt = salt,
        iterations =100000,
        backend = default_backend())
    return kdf

def askPassword():
        password = getpass.getpass() #Pede a password como input
        return str.encode(password)

# message authentication code
def mac(key,source, tag=None):
    h = hmac.HMAC(key,hashes.SHA256(),default_backend())
    h.update(source)
    if tag == None:
        return h.finalize()
    h.verify(tag)

#função hash
def Hash(s):
    digest = hashes.Hash(hashes.SHA256(),backend=default_backend())
    digest.update(s)
    return digest.finalize()

class Emitter:
    """ Classe que implementa a funcionalidade de um Emitter. """
    def __init__(self):
        """ Construtor da classe. """
        self.socket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        self.dest = ('127.0.0.1', 5000)
    
    def encription(self,key,msg):
        iv = os.urandom(16)
        cipher = Cipher(algorithms.AES(key), modes.GCM(iv), default_backend())
        encryptor = cipher.encryptor()
        encripted_text = encryptor.update(msg) + encryptor.finalize()
        return iv,encripted_text,encryptor.tag
    
    def askMessage(self):
        print('Input message to send (empty to finish)') #pede a mensagem
        return input().encode()
    
    def server_connection(self):
        self.socket.connect(self.dest)
        print("\n\n Cliente connectado na porta: 5000 \n\n")
    
    def endConnection(self):
        self.socket.close()
        print('\n Conexão terminada. \n')
    
    def run(self):
        self.server_connection() #Conecta-se ao Servidor
        password = askPassword()
        salt = os.urandom(16)
        key = passKDF(salt).derive(password)
        
        while True:
            msg = self.askMessage()
            
            try:
                
                tagPT = mac(Hash(key),msg)

                iv,ciphertext,tagCT = self.encription(key,msg)
            
                new_msg = salt + tagPT + iv + tagCT + ciphertext
                if(len(new_msg)>0):
                    self.socket.send(new_msg)
                else:
                    self.endConnection()
            except:
                print("Erro no Emissor")

def mainEmitter():
    #erro
    emitter = Emitter()
    emitter.run()

mainEmitter()