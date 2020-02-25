from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes, hmac
from cryptography.exceptions import InvalidSignature
import getpass
import socket
import os

max_msg_size = 9999

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


class Receiver:
    """ Classe que implementa a funcionalidade de um Receiver. """
    def __init__(self):
        """ Construtor da classe. """
        self.socket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        self.orig = ('', 5000) 
    
    def startSocket(self):
        self.socket.bind(self.orig)
        self.socket.listen(1)
        print("\n\n Servidor à escuta na porta: 5000 \n\n")
    
    def decription(self,key,iv,tag,msg):
        cipher = Cipher(algorithms.AES(key),modes.GCM(iv,tag),default_backend()) 
        decryptor = cipher.decryptor()
        plaintext = decryptor.update(msg) + decryptor.finalize()
        return plaintext 
    
    def run(self):
        print('Receiver RUN')
        self.startSocket()
        i = 0
        while(i < 1): 
            con, cliente = self.socket.accept()
            print("Conectado por: ", cliente)
            i+=1
            password = askPassword()
            
            while True:
                msg = con.recv(max_msg_size)
                if (not msg):
                    break
                else:
                    salt = msg[0:16]
                    tagK = msg[16:48]
                    iv = msg[48:64]
                    tag = msg[64:80]
                    ciphertext = msg[80:]
                    
                    key = passKDF(salt).derive(password)
                    
                    try:
                        plaintext = self.decription(key,iv,tag,ciphertext)
                        if (tagK == mac(Hash(key),plaintext)):
                            print(plaintext.decode())
                        else:
                            print('Mensagem comprometida. Chave não autenticada')   
                    except:
                        print('Mensagem comprometida\n')
                        self.breakCon(con)          
            self.breakCon(con)
        return 
    
    def breakCon(self,con):
        con.close()
        print("\n\nConexão fechada\n\n")
        return

def mainReceiver():
    #erro
    receiver = Receiver()
    receiver.run()
    return

mainReceiver()