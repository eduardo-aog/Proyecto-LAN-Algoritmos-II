# Módulo 1: Dispositivos y Red - Clases Device e Interface
# Representa los dispositivos de red y sus interfaces

from estructuras_datos import ListaEnlazada, Cola, Pila
import re

class Interfaz:
    """Representa una interfaz de red de un dispositivo"""
    
    def __init__(self, nombre, dispositivo_padre):
        self.nombre = nombre
        self.dispositivo_padre = dispositivo_padre
        self.direccion_ip = None
        self.activa = False  # Estado shutdown por defecto
        self.vecinos = ListaEnlazada()  # Interfaces conectadas
        self.cola_entrada = Cola()  # Paquetes entrantes
        self.cola_salida = Cola()   # Paquetes salientes
    
    def asignar_ip(self, ip):
        """Asigna dirección IP a la interfaz con validación"""
        if self._validar_ip(ip):
            self.direccion_ip = ip
            return True
        return False
    
    def _validar_ip(self, ip):
        """Valida formato de dirección IP"""
        patron = r'^(\d{1,3}\.){3}\d{1,3}$'
        if not re.match(patron, ip):
            return False
        
        octetos = ip.split('.')
        for octeto in octetos:
            if not (0 <= int(octeto) <= 255):
                return False
        return True
    
    def activar(self):
        """Activa la interfaz (no shutdown)"""
        self.activa = True
    
    def desactivar(self):
        """Desactiva la interfaz (shutdown)"""
        self.activa = False
    
    def conectar_vecino(self, interfaz_vecina):
        """Conecta esta interfaz con otra"""
        if not self.vecinos.buscar(interfaz_vecina):
            self.vecinos.agregar(interfaz_vecina)
    
    def desconectar_vecino(self, interfaz_vecina):
        """Desconecta esta interfaz de otra"""
        self.vecinos.eliminar(interfaz_vecina)
    
    def obtener_vecinos(self):
        """Retorna lista de interfaces vecinas"""
        return self.vecinos.obtener_lista()
    
    def recibir_paquete(self, paquete):
        """Recibe un paquete en la cola de entrada"""
        if self.activa:
            self.cola_entrada.encolar(paquete)
            return True
        return False
    
    def enviar_paquete(self, paquete):
        """Envía un paquete a la cola de salida"""
        if self.activa:
            self.cola_salida.encolar(paquete)
            return True
        return False
    
    def procesar_cola_salida(self):
        """Procesa un paquete de la cola de salida"""
        if not self.cola_salida.esta_vacia() and self.activa:
            return self.cola_salida.desencolar()
        return None
    
    def procesar_cola_entrada(self):
        """Procesa un paquete de la cola de entrada"""
        if not self.cola_entrada.esta_vacia() and self.activa:
            return self.cola_entrada.desencolar()
        return None
    
    def obtener_estado(self):
        """Retorna información del estado de la interfaz"""
        return {
            'nombre': self.nombre,
            'ip': self.direccion_ip or 'No asignada',
            'estado': 'up' if self.activa else 'down',
            'vecinos': len(self.vecinos.obtener_lista()),
            'cola_entrada': self.cola_entrada.obtener_tamaño(),
            'cola_salida': self.cola_salida.obtener_tamaño()
        }

class Dispositivo:
    """Clase base para todos los dispositivos de red"""
    
    def __init__(self, nombre, tipo_dispositivo):
        self.nombre = nombre
        self.tipo = tipo_dispositivo
        self.interfaces = {}  # Diccionario de interfaces
        self.en_linea = True
        self.historial_recibidos = Pila()  # Historial de paquetes recibidos
        self.paquetes_procesados = 0
        self.paquetes_enviados = 0
        self.paquetes_descartados = 0
    
    def cambiar_nombre(self, nuevo_nombre):
        """Cambia el nombre del dispositivo"""
        if nuevo_nombre and isinstance(nuevo_nombre, str):
            self.nombre = nuevo_nombre
            return True
        return False
    
    def agregar_interfaz(self, nombre_interfaz):
        """Agrega una nueva interfaz al dispositivo"""
        if nombre_interfaz not in self.interfaces:
            self.interfaces[nombre_interfaz] = Interfaz(nombre_interfaz, self)
            return True
        return False
    
    def obtener_interfaz(self, nombre_interfaz):
        """Obtiene una interfaz específica"""
        return self.interfaces.get(nombre_interfaz)
    
    def configurar_interfaz_ip(self, nombre_interfaz, ip):
        """Configura IP en una interfaz específica"""
        interfaz = self.obtener_interfaz(nombre_interfaz)
        if interfaz:
            return interfaz.asignar_ip(ip)
        return False
    
    def activar_interfaz(self, nombre_interfaz):
        """Activa una interfaz específica"""
        interfaz = self.obtener_interfaz(nombre_interfaz)
        if interfaz:
            interfaz.activar()
            return True
        return False
    
    def desactivar_interfaz(self, nombre_interfaz):
        """Desactiva una interfaz específica"""
        interfaz = self.obtener_interfaz(nombre_interfaz)
        if interfaz:
            interfaz.desactivar()
            return True
        return False
    
    def establecer_estado(self, en_linea):
        """Establece si el dispositivo está online u offline"""
        self.en_linea = en_linea
    
    def procesar_paquetes(self):
        """Procesa paquetes en todas las interfaces activas"""
        paquetes_procesados = []
        
        if not self.en_linea:
            return paquetes_procesados
        
        # Procesar colas de entrada de todas las interfaces
        for interfaz in self.interfaces.values():
            paquete = interfaz.procesar_cola_entrada()
            if paquete:
                self.paquetes_procesados += 1
                paquete.agregar_salto(self.nombre)
                
                # Si el paquete es para este dispositivo
                if self._es_paquete_para_mi(paquete):
                    paquete.marcar_entregado()
                    self.historial_recibidos.apilar(paquete)
                else:
                    # Reenviar paquete
                    if paquete.decrementar_ttl():
                        interfaz_salida = self._encontrar_ruta(paquete.destino)
                        if interfaz_salida:
                            interfaz_salida.enviar_paquete(paquete)
                        else:
                            paquete.descartado = True
                            paquete.razon_descarte = "No hay ruta al destino"
                            self.paquetes_descartados += 1
                    else:
                        self.paquetes_descartados += 1
                
                paquetes_procesados.append(paquete)
        
        # Procesar colas de salida - enviar paquetes a vecinos
        for interfaz in self.interfaces.values():
            if interfaz.activa:
                paquete_salida = interfaz.procesar_cola_salida()
                if paquete_salida:
                    # Enviar a todas las interfaces vecinas
                    vecinos = interfaz.obtener_vecinos()
                    if vecinos:
                        # Enviar al primer vecino disponible (routing simple)
                        vecino = vecinos[0]
                        if vecino.activa:
                            vecino.recibir_paquete(paquete_salida)
                            self.paquetes_enviados += 1
                    else:
                        # No hay vecinos, descartar paquete
                        paquete_salida.descartado = True
                        paquete_salida.razon_descarte = "No hay vecinos conectados"
                        self.paquetes_descartados += 1
        
        return paquetes_procesados
    
    def _es_paquete_para_mi(self, paquete):
        """Verifica si el paquete está destinado a este dispositivo"""
        for interfaz in self.interfaces.values():
            if interfaz.direccion_ip == paquete.destino:
                return True
        return False
    
    def _encontrar_ruta(self, ip_destino):
        """Encuentra la interfaz de salida para un destino (routing simple)"""
        # Implementación básica: usar la primera interfaz activa con vecinos
        for interfaz in self.interfaces.values():
            if interfaz.activa and not interfaz.vecinos.esta_vacia():
                return interfaz
        return None
    
    def enviar_paquete(self, ip_origen, ip_destino, mensaje, ttl=64):
        """Envía un paquete desde este dispositivo"""
        from paquete import Paquete
        
        if not self.en_linea:
            return False
        
        # Encontrar interfaz con la IP origen
        interfaz_origen = None
        for interfaz in self.interfaces.values():
            if interfaz.direccion_ip == ip_origen and interfaz.activa:
                interfaz_origen = interfaz
                break
        
        if not interfaz_origen:
            return False
        
        # Crear y enviar paquete
        paquete = Paquete(ip_origen, ip_destino, mensaje, ttl)
        paquete.agregar_salto(self.nombre)
        
        if interfaz_origen.enviar_paquete(paquete):
            self.paquetes_enviados += 1
            return True
        
        return False
    
    def obtener_estadisticas(self):
        """Retorna estadísticas del dispositivo"""
        return {
            'nombre': self.nombre,
            'tipo': self.tipo,
            'estado': 'online' if self.en_linea else 'offline',
            'interfaces': len(self.interfaces),
            'paquetes_procesados': self.paquetes_procesados,
            'paquetes_enviados': self.paquetes_enviados,
            'paquetes_descartados': self.paquetes_descartados,
            'historial_size': self.historial_recibidos.obtener_tamaño()
        }
    
    def obtener_historial(self):
        """Retorna el historial de paquetes recibidos"""
        return self.historial_recibidos.obtener_elementos()
    
    def obtener_info_interfaces(self):
        """Retorna información de todas las interfaces"""
        info = {}
        for nombre, interfaz in self.interfaces.items():
            info[nombre] = interfaz.obtener_estado()
        return info
    
    def obtener_colas_info(self):
        """Retorna información de las colas de todas las interfaces"""
        info = {}
        for nombre, interfaz in self.interfaces.items():
            info[nombre] = {
                'entrada': interfaz.cola_entrada.obtener_elementos(),
                'salida': interfaz.cola_salida.obtener_elementos()
            }
        return info
