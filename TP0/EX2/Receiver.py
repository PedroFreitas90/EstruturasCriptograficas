from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes, hmac
from cryptography.exceptions import InvalidSignature
import getpass
import socket
import os

max_msg_size = 9999

HOST = ''     # Endereco IP do Servidor
PORT = 5000  # Porta que o Servidor esta

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


class Receiver:
    """ Classe que implementa a funcionalidade de um Receiver. """
    def __init__(self):
        """ Construtor da classe. """
        self.socket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        self.orig = (HOST, PORT) 
    
    def startSocket(self):
        self.socket.bind(self.orig)
        self.socket.listen(1)
        print("\n\n Servidor à escuta na porta: " + str(PORT) + "\n\n")
    
    def askPassword(self):
        password = getpass.getpass() #Pede a password como input
        return str.encode(password)
    
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
                    iv = msg[16:32]
                    tag = msg[32:48]
                    ciphertext = msg[48:]
                    
                    key = passKDF(salt).derive(password)
                    
                    try:
                        plaintext = self.decription(key,iv,tag,ciphertext)
                        print(plaintext.decode())
                        
                    except:
                        print('Mensagem comprometida\n')
                        self.breakCon(con)          
            self.breakCon(con)
        return 
    
    def breakCon(self,con):
        con.close()
        print("\n\nConexão fechada\n\n")
        return

def main():
    receiver = Receiver()
    receiver.run()
    return

main()