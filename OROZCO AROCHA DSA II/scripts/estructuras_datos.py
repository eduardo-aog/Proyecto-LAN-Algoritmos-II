# Módulo 3: Estructuras de Datos
# Implementación de listas enlazadas, pilas y colas desde cero

class Nodo:
    """Nodo básico para estructuras enlazadas"""
    def __init__(self, dato):
        self.dato = dato
        self.siguiente = None

class ListaEnlazada:
    """Lista enlazada simple para almacenar vecinos de interfaces"""
    def __init__(self):
        self.cabeza = None
        self.tamaño = 0
    
    def agregar(self, dato):
        """Agrega un elemento al final de la lista"""
        nuevo_nodo = Nodo(dato)
        if not self.cabeza:
            self.cabeza = nuevo_nodo
        else:
            actual = self.cabeza
            while actual.siguiente:
                actual = actual.siguiente
            actual.siguiente = nuevo_nodo
        self.tamaño += 1
    
    def eliminar(self, dato):
        """Elimina un elemento específico de la lista"""
        if not self.cabeza:
            return False
        
        if self.cabeza.dato == dato:
            self.cabeza = self.cabeza.siguiente
            self.tamaño -= 1
            return True
        
        actual = self.cabeza
        while actual.siguiente:
            if actual.siguiente.dato == dato:
                actual.siguiente = actual.siguiente.siguiente
                self.tamaño -= 1
                return True
            actual = actual.siguiente
        return False
    
    def buscar(self, dato):
        """Busca un elemento en la lista"""
        actual = self.cabeza
        while actual:
            if actual.dato == dato:
                return True
            actual = actual.siguiente
        return False
    
    def obtener_lista(self):
        """Retorna todos los elementos como lista de Python para facilitar iteración"""
        elementos = []
        actual = self.cabeza
        while actual:
            elementos.append(actual.dato)
            actual = actual.siguiente
        return elementos
    
    def esta_vacia(self):
        return self.cabeza is None

class Cola:
    """Cola FIFO para gestionar paquetes entrantes y salientes"""
    def __init__(self):
        self.frente = None
        self.final = None
        self.tamaño = 0
    
    def encolar(self, dato):
        """Agrega un elemento al final de la cola"""
        nuevo_nodo = Nodo(dato)
        if not self.final:
            self.frente = self.final = nuevo_nodo
        else:
            self.final.siguiente = nuevo_nodo
            self.final = nuevo_nodo
        self.tamaño += 1
    
    def desencolar(self):
        """Remueve y retorna el primer elemento de la cola"""
        if not self.frente:
            return None
        
        dato = self.frente.dato
        self.frente = self.frente.siguiente
        if not self.frente:
            self.final = None
        self.tamaño -= 1
        return dato
    
    def esta_vacia(self):
        return self.frente is None
    
    def obtener_tamaño(self):
        return self.tamaño
    
    def obtener_elementos(self):
        """Retorna todos los elementos sin removerlos"""
        elementos = []
        actual = self.frente
        while actual:
            elementos.append(actual.dato)
            actual = actual.siguiente
        return elementos

class Pila:
    """Pila LIFO para historial de mensajes recibidos"""
    def __init__(self):
        self.cima = None
        self.tamaño = 0
    
    def apilar(self, dato):
        """Agrega un elemento a la cima de la pila"""
        nuevo_nodo = Nodo(dato)
        nuevo_nodo.siguiente = self.cima
        self.cima = nuevo_nodo
        self.tamaño += 1
    
    def desapilar(self):
        """Remueve y retorna el elemento de la cima"""
        if not self.cima:
            return None
        
        dato = self.cima.dato
        self.cima = self.cima.siguiente
        self.tamaño -= 1
        return dato
    
    def obtener_cima(self):
        """Retorna el elemento de la cima sin removerlo"""
        return self.cima.dato if self.cima else None
    
    def esta_vacia(self):
        return self.cima is None
    
    def obtener_tamaño(self):
        return self.tamaño
    
    def obtener_elementos(self):
        """Retorna todos los elementos desde la cima hacia abajo"""
        elementos = []
        actual = self.cima
        while actual:
            elementos.append(actual.dato)
            actual = actual.siguiente
        return elementos
