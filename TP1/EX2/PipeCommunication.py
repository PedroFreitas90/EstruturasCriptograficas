#/usr/bin/python3

from multiprocessing import Pipe, Process

class PipeCommunication:
    def __init__(self,leftE, rightE, timeout=None):
        '''
            Classe responsável por ligar 2 entidades através de um Pipe para poderem comunicar entre si.
            A cada entidade será atribuída uma extremidado do pipe.
            Será criado um processo para cada entidade onde o processo terá como alvo a entidade respetiva e 
                passar-lhe-á como argumento a extremidade da conexão que lhe é correspondente. 
        '''
        left_end, right_end = Pipe()
        self.timeout = timeout
        self.left_Process = Process(target=leftE, args=(left_end,))
        self.right_Process = Process(target=rightE, args=(right_end,))
    
    def run(self):
        self.left_Process.start()
        self.right_Process.start()
        self.left_Process.join(self.timeout)
        self.right_Process.join(self.timeout)

def leftE(conn):
	print('LeftE: I am leftE! Sending message!')
	conn.send(b'Ola eu sou a entidade da Esquerda!')
	conn.close()

def rightE(conn):
	print('RightE: Eu sou a RightE! Receiveng messages!')
	msg = conn.recv()
	print('RightE leu: ' + msg.decode())
	conn.close()
	try:
		print(conn.recv())
	except: 
		print('Conexão já foi fechada! Não há nada para ler')

def teste():
    PipeCommunication(leftE,rightE,timeout=30).run()
