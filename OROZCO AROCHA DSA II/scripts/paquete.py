# Módulo 2: Paquetes y Comunicación
# Definición de la estructura de paquetes de red

import uuid
import time

class Paquete:
    """Representa un paquete de red virtual con toda su información"""
    
    def __init__(self, origen, destino, contenido, ttl=64):
        self.id_unico = str(uuid.uuid4())[:8]  # Identificador único corto
        self.origen = origen
        self.destino = destino
        self.contenido = contenido
        self.ttl_inicial = ttl
        self.ttl_actual = ttl
        self.traza_ruta = []  # Lista de dispositivos por los que ha pasado
        self.timestamp = time.time()
        self.entregado = False
        self.descartado = False
        self.razon_descarte = None
    
    def decrementar_ttl(self):
        """Decrementa el TTL en 1 y verifica si debe descartarse"""
        self.ttl_actual -= 1
        if self.ttl_actual <= 0:
            self.descartado = True
            self.razon_descarte = "TTL expirado"
            return False
        return True
    
    def agregar_salto(self, dispositivo):
        """Agrega un dispositivo a la traza de ruta"""
        self.traza_ruta.append(dispositivo)
    
    def obtener_traza_formateada(self):
        """Retorna la traza de ruta como string formateado"""
        if not self.traza_ruta:
            return "Sin traza"
        return " → ".join(self.traza_ruta)
    
    def marcar_entregado(self):
        """Marca el paquete como entregado exitosamente"""
        self.entregado = True
    
    def obtener_info_completa(self):
        """Retorna información completa del paquete para reportes"""
        return {
            'id': self.id_unico,
            'origen': self.origen,
            'destino': self.destino,
            'contenido': self.contenido,
            'ttl_inicial': self.ttl_inicial,
            'ttl_actual': self.ttl_actual,
            'traza': self.obtener_traza_formateada(),
            'entregado': self.entregado,
            'descartado': self.descartado,
            'razon_descarte': self.razon_descarte,
            'saltos': len(self.traza_ruta)
        }
    
    def __str__(self):
        estado = "Entregado" if self.entregado else ("Descartado" if self.descartado else "En tránsito")
        return f"Paquete {self.id_unico}: {self.origen} → {self.destino} | TTL: {self.ttl_actual} | Estado: {estado}"
