from datetime import datetime

# Modelo básico de Vuelo (no es el de SQLAlchemy aún)
class Vuelo:
    def __init__(self, codigo, estado, hora, origen, destino):
        self.codigo = codigo
        self.estado = estado  # "programado", "emergencia", "retrasado"
        self.hora = hora
        self.origen = origen
        self.destino = destino

    def __repr__(self):
        return f"<Vuelo {self.codigo} | {self.estado} | {self.origen} → {self.destino}>"


# Nodo de la lista doblemente enlazada
class Nodo:
    def __init__(self, vuelo):
        self.vuelo = vuelo
        self.anterior = None
        self.siguiente = None


# Lista doblemente enlazada
class ListaVuelos:
    def __init__(self):
        self.cabeza = None
        self.contador = 0

    def insertar_al_frente(self, vuelo):
        nuevo = Nodo(vuelo)
        if self.cabeza:
            self.cabeza.anterior = nuevo
            nuevo.siguiente = self.cabeza
        self.cabeza = nuevo
        self.contador += 1

    def insertar_al_final(self, vuelo):
        nuevo = Nodo(vuelo)
        if not self.cabeza:
            self.cabeza = nuevo
        else:
            actual = self.cabeza
            while actual.siguiente:
                actual = actual.siguiente
            actual.siguiente = nuevo
            nuevo.anterior = actual
        self.contador += 1

    def obtener_primero(self):
        return self.cabeza.vuelo if self.cabeza else None

    def obtener_ultimo(self):
        actual = self.cabeza
        if not actual:
            return None
        while actual.siguiente:
            actual = actual.siguiente
        return actual.vuelo

    def longitud(self):
        return self.contador

    def insertar_en_posicion(self, vuelo, posicion):
        if posicion <= 0:
            self.insertar_al_frente(vuelo)
        elif posicion >= self.contador:
            self.insertar_al_final(vuelo)
        else:
            nuevo = Nodo(vuelo)
            actual = self.cabeza
            for _ in range(posicion):
                actual = actual.siguiente
            anterior = actual.anterior
            anterior.siguiente = nuevo
            nuevo.anterior = anterior
            nuevo.siguiente = actual
            actual.anterior = nuevo
            self.contador += 1

    def extraer_de_posicion(self, posicion):
        if posicion < 0 or posicion >= self.contador:
            return None
        actual = self.cabeza
        for _ in range(posicion):
            actual = actual.siguiente
        if actual.anterior:
            actual.anterior.siguiente = actual.siguiente
        else:
            self.cabeza = actual.siguiente
        if actual.siguiente:
            actual.siguiente.anterior = actual.anterior
        self.contador -= 1
        return actual.vuelo

    def obtener_lista(self):
        vuelos = []
        actual = self.cabeza
        while actual:
            vuelos.append(actual.vuelo)
            actual = actual.siguiente
        return vuelos
