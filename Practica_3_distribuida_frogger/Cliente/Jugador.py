from multiprocessing.connection import Client
from tkinter import ttk, simpledialog, messagebox
import traceback
import pygame
import sys, os

WHITE = (255, 255, 255)

tamVentana = (700, 525)
X, Y = 0, 1

SourceRana = ["ranaD.png", "ranaI.png"] #Para que la rana mire al lado al que avanza
ladoStr = ["Derecha", "Izquierda"]

"""
Clase para gestionar la información de cada jugador: el lado desde el que juega y 
la posición en la que se encuentra.
"""
class Jugador():
    def __init__(self, lado):
        self.lado = lado
        self.pos = [None, None]

    def get_pos(self):
        return self.pos

    def get_lado(self):
        return self.lado

    def set_pos(self, pos):
        self.pos = pos

    def __str__(self):
        return f"P<{ladoStr[self.lado], self.pos}>"

"""
Clase para gestionar la información de cada obstáculo: la posición en la que se encuentra.
"""
class Obstaculo():
    def __init__(self):
        self.pos=[ None, None ]

    def get_pos(self):
        return self.pos

    def set_pos(self, pos):
        self.pos = pos

    def __str__(self):
        return f"B<{self.pos}>"

"""
Clase para gestionar la información del estado de un juego: los jugadores, los obstáculos, 
la puntuación y el estado de juego (jugando o no)
"""
class JuegoO():
    def __init__(self):
        self.Jugadores = [Jugador(i) for i in range(2)]
        self.Obstaculos = [Obstaculo(), Obstaculo(), Obstaculo(), Obstaculo()]
        self.puntuacion = [0,0]
        self.jugando = True

    def get_Jugador(self, lado):
        return self.Jugadores[lado]

    def set_pos_Jugador(self, lado, pos):
        self.Jugadores[lado].set_pos(pos)

    def get_Obstaculo(self):
        return self.Obstaculos

    def set_Obstaculo_pos(self, pos):
        for i in range(len(pos)):
            self.Obstaculos[i].set_pos(pos[i])

    def get_puntuacion(self):
        return self.puntuacion

    def set_puntuacion(self, puntuacion):
        self.puntuacion = puntuacion

    def update(self, Juegoinfo):
        self.set_pos_Jugador(0, Juegoinfo['pos_0'])
        self.set_pos_Jugador(1, Juegoinfo['pos_1'])
        self.set_Obstaculo_pos(Juegoinfo['pos_Obstaculo'])
        self.set_puntuacion(Juegoinfo['puntuacion'])
        self.jugando = Juegoinfo['jugando']

    def is_jugando(self):
        return self.jugando

    def stop(self):
        self.jugando = False

    def __str__(self):
        return f"G<{self.Jugadores[1]}:{self.Jugadores[0]}:{self.Obstaculo}>"

"""
Clase para gestionar el sprite del jugador: la imagen de la rana correspondiente a su lado, 
que se muestra en la posición en la que se encuentre el jugador.
"""
class Rana(pygame.sprite.Sprite):
    def __init__(self, Jugador):
      super().__init__()
      self.image = pygame.image.load(SourceRana[Jugador.get_lado()])
      self.Jugador = Jugador
      self.rect = self.image.get_rect()
      self.update()

    def update(self):
        pos = self.Jugador.get_pos()
        self.rect.centerx, self.rect.centery = pos

    def __str__(self):
        return f"S<{self.Jugador}>"

"""
Clase para gestionar el sprite del jugador: la imagen del coche, 
que se muestra en la posición en la que se encuentre el obstaculo.
"""
class ObstaculoSprite(pygame.sprite.Sprite):
    def __init__(self, Obstaculo):
        super().__init__()
        self.Obstaculo = Obstaculo
        self.image = pygame.image.load("lillambo.png")
        self.rect = self.image.get_rect()
        self.update()

    def update(self):
        pos = self.Obstaculo.get_pos()
        self.rect.centerx, self.rect.centery = pos
"""
Clase para gestionar la ventana de un juego: de fondo dos carreteras, sobre las que se mueven los sprites de los obstaculos.
Gestiona las acciones del jugador y las actualizaciones que recibe de la sala de juegos para mostrar por pantalla el estado del juego.
También tiene el método correspondiente a la pantalla de fin de juego donde se muestra la puntuación y si el jugador ha ganado o perdido.
"""
class Display():
    def __init__(self, Juego):
        self.Juego = Juego
        self.ranas = [Rana(self.Juego.get_Jugador(i)) for i in range(2)] #Nos creamos el objeto rana para cada jugador
        self.obstaculos = [ObstaculoSprite(obs) for obs in self.Juego.get_Obstaculo()] #Nos creamos l objeto obstaculoSprite para cada obstaculo
        self.obstaculo_group = pygame.sprite.Group()
        self.rana_group = pygame.sprite.Group()
        self.all_sprites = pygame.sprite.Group()
        for rana  in self.ranas: #Agrupamos todos los jugadores
            self.rana_group.add(rana)
            self.all_sprites.add(rana)
        for obstaculo in self.obstaculos: #Agrupamos odos los obstaculos
            self.obstaculo_group.add(obstaculo)
            self.all_sprites.add(obstaculo)

        self.screen = pygame.display.set_mode(tamVentana)
        self.clock =  pygame.time.Clock() 
        self.background = pygame.image.load('background.png')
        pygame.init()

    """
    Función que recolecta las acciones que recibe el juego y devuelve la lista con ellas:
    - Tecla flecha derecha o izquierda: Avanzar. Encolamos: A
    - Tecla flecha arriba Subir. Encolamos: U
    - Tecla flecha abajo: Bajar. Encolamos: D
    - Tecla escape o salir del juego: Salir. Encolamos: Q
    - Si el jugador choca con algun obstaculo: Encolamos: la posición de ese obstáculo en la lista
    """
    def analyze_events(self, lado):
        events = []
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    events.append("Q")
                elif event.key == pygame.K_UP:
                    events.append("U")
                elif event.key == pygame.K_DOWN:
                    events.append("D")
                elif event.key == pygame.K_LEFT:
                    events.append("A")
                elif event.key == pygame.K_RIGHT:
                    events.append("A")
            elif event.type == pygame.QUIT:
                events.append("Q")
        for i in range(len(self.obstaculos)):
            if pygame.sprite.collide_rect(self.obstaculos[i], self.ranas[lado]):
                events.append(i)
        return events
"""
Método encargado de actualizar la pantalla con las puntuaciones y posiciones de los sprites correspondientes
"""
    def refresh(self):
        self.all_sprites.update()
        self.screen.blit(self.background, (0, 0))
        puntuacion = self.Juego.get_puntuacion()
        font = pygame.font.Font(None, 74)
        text = font.render(f"{puntuacion[0]}", 1, WHITE)
        self.screen.blit(text, (250, 10))
        text = font.render(f"{puntuacion[1]}", 1, WHITE)
        self.screen.blit(text, (tamVentana[X]-250, 10))
        self.all_sprites.draw(self.screen)
        pygame.display.flip()

    def tick(self):
        self.clock.tick(60)
"""
Método que muestra por pantalla la puntuación y si el jugador ha ganado o perdido
"""
    def gameOver(self, lado):
        puntuacion = self.Juego.get_puntuacion()
        winLose = "Perdido" if puntuacion[lado]<puntuacion[(lado+1)%2] else "Ganado"
        messagebox.showinfo(f'Has {winLose}', f"Has {winLose}. \n Puntuacion: {puntuacion}")

    @staticmethod
    def quit():
        pygame.quit()

 """
 Funcion para cuando se inicia el juego directamente en vez de desde el chat
 """
def main(ip_address):
    try:
        with Client((ip_address, 6000), authkey=b'secret password') as conn:
            empiezaJuego(conn)
    except:
        traceback.print_exc()
"""
Funcion que crea un objeto juego y otro display para manejar un juego con el jugador cuya conexión recibe como argumento.
Muestra la pantalla de game Over una vez acaba el juego, que hay que cerrar para que se cierre la ventana de juego.
"""
def empiezaJuego(conn):
    Juego = JuegoO()
    print('conectado')
    lado = conn.recv()
    Juegoinfo = conn.recv()
    print(f"Jugando en {ladoStr[lado]}")
    Juego.update(Juegoinfo)
    display = Display(Juego)
    while Juego.is_jugando():
        events = display.analyze_events(lado)
        for ev in events:
            conn.send(ev)
            if ev == 'Q':
                Juego.stop()
        conn.send("N")
        Juegoinfo = conn.recv()
        Juego.update(Juegoinfo)
        display.refresh()
        display.tick()
    display.gameOver(lado)
    pygame.quit()

    """
    Si se ejecuta directamente el juego y no desde chat, se puede añadir el argumento con la direccion del servidor.
    Por defecto usa la propia.
    """
if __name__=="__main__":   
    getArg = lambda pD, numArg: pD if len(sys.argv) <= numArg else sys.argv[numArg]
    main(getArg("127.0.0.1", 1))
