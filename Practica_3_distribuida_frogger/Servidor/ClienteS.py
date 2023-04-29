from multiprocessing import Value, Condition

"""

Gestión de usuarios en chat, notificaciones, recepción de información,
salida y cierre mediante variables condición y valores.

"""


class Cliente():
    def __init__(self, conn, usuario):
        self.conn = conn
        self.usuario = usuario
        print ('Nombre de usuario', usuario)
        self.enChat = Value('i', 1)
        self.cond = Condition()
        
    def getConn(self):
        return self.conn
    def getUsuario(self):
        return self.usuario
    def estaEnChat(self):
        return self.enChat.value == 1
    def setEnChat(self, n):
        self.enChat.value = 0
    def espera(self):
        with self.cond:
            self.cond.wait()  
    def notifica(self):
        with self.cond:
            self.cond.notify_all()  
    def salir(self):
        self.conn.close() 
    def send(self, m1):
        self.conn.send(m1)
    def recv(self):
        return self.conn.recv()
    def close(self):
        seld.conn.close()
