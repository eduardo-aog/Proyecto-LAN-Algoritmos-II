# Módulo 1: Dispositivos y Red - Clase Network
# Orquesta el conjunto de dispositivos y sus conexiones

from dispositivo import Dispositivo
from estructuras_datos import ListaEnlazada

class Red:
    """Gestiona la topología completa de la red"""
    
    def __init__(self):
        self.dispositivos = {}  # Diccionario de dispositivos por nombre
        self.conexiones = ListaEnlazada()  # Lista de conexiones activas
        self.estadisticas_globales = {
            'paquetes_totales_enviados': 0,
            'paquetes_entregados': 0,
            'paquetes_descartados_ttl': 0,
            'paquetes_descartados_ruta': 0,
            'total_saltos': 0,
            'dispositivo_mas_activo': None,
            'max_paquetes_procesados': 0
        }
    
    def agregar_dispositivo(self, nombre, tipo_dispositivo):
        """Agrega un nuevo dispositivo a la red"""
        if nombre not in self.dispositivos:
            self.dispositivos[nombre] = Dispositivo(nombre, tipo_dispositivo)
            
            # Agregar interfaces por defecto según el tipo
            if tipo_dispositivo.lower() == 'router':
                self.dispositivos[nombre].agregar_interfaz('g0/0')
                self.dispositivos[nombre].agregar_interfaz('g0/1')
            elif tipo_dispositivo.lower() == 'switch':
                for i in range(4):  # 4 puertos por defecto
                    self.dispositivos[nombre].agregar_interfaz(f'g0/{i}')
            elif tipo_dispositivo.lower() in ['pc', 'host']:
                self.dispositivos[nombre].agregar_interfaz('eth0')
            elif tipo_dispositivo.lower() == 'firewall':
                self.dispositivos[nombre].agregar_interfaz('inside')
                self.dispositivos[nombre].agregar_interfaz('outside')
            
            return True
        return False
    
    def obtener_dispositivo(self, nombre):
        """Obtiene un dispositivo específico"""
        return self.dispositivos.get(nombre)
    
    def conectar_dispositivos(self, dispositivo1, interfaz1, dispositivo2, interfaz2):
        """Conecta dos interfaces de dispositivos diferentes"""
        disp1 = self.obtener_dispositivo(dispositivo1)
        disp2 = self.obtener_dispositivo(dispositivo2)
        
        if not disp1 or not disp2:
            return False
        
        int1 = disp1.obtener_interfaz(interfaz1)
        int2 = disp2.obtener_interfaz(interfaz2)
        
        if not int1 or not int2:
            return False
        
        # Crear conexión bidireccional
        int1.conectar_vecino(int2)
        int2.conectar_vecino(int1)
        
        # Registrar conexión
        conexion = f"{dispositivo1}:{interfaz1} <-> {dispositivo2}:{interfaz2}"
        self.conexiones.agregar(conexion)
        
        return True
    
    def desconectar_dispositivos(self, dispositivo1, interfaz1, dispositivo2, interfaz2):
        """Desconecta dos interfaces de dispositivos"""
        disp1 = self.obtener_dispositivo(dispositivo1)
        disp2 = self.obtener_dispositivo(dispositivo2)
        
        if not disp1 or not disp2:
            return False
        
        int1 = disp1.obtener_interfaz(interfaz1)
        int2 = disp2.obtener_interfaz(interfaz2)
        
        if not int1 or not int2:
            return False
        
        # Remover conexión bidireccional
        int1.desconectar_vecino(int2)
        int2.desconectar_vecino(int1)
        
        # Remover registro de conexión
        conexion = f"{dispositivo1}:{interfaz1} <-> {dispositivo2}:{interfaz2}"
        self.conexiones.eliminar(conexion)
        
        return True
    
    def establecer_estado_dispositivo(self, nombre, en_linea):
        """Establece el estado online/offline de un dispositivo"""
        dispositivo = self.obtener_dispositivo(nombre)
        if dispositivo:
            dispositivo.establecer_estado(en_linea)
            return True
        return False
    
    def procesar_tick(self):
        """Procesa un tick de simulación en toda la red"""
        todos_paquetes = []
        
        # Procesar cada dispositivo múltiples veces para asegurar flujo de paquetes
        for _ in range(2):  # Procesar 2 veces por tick para mejor flujo
            for dispositivo in self.dispositivos.values():
                paquetes = dispositivo.procesar_paquetes()
                todos_paquetes.extend(paquetes)
        
        # Actualizar estadísticas globales
        self._actualizar_estadisticas(todos_paquetes)
        
        return todos_paquetes
    
    def _actualizar_estadisticas(self, paquetes):
        """Actualiza las estadísticas globales de la red"""
        for paquete in paquetes:
            info = paquete.obtener_info_completa()
            
            if info['entregado']:
                self.estadisticas_globales['paquetes_entregados'] += 1
                self.estadisticas_globales['total_saltos'] += info['saltos']
            
            if info['descartado']:
                if info['razon_descarte'] == 'TTL expirado':
                    self.estadisticas_globales['paquetes_descartados_ttl'] += 1
                else:
                    self.estadisticas_globales['paquetes_descartados_ruta'] += 1
        
        # Encontrar dispositivo más activo
        max_procesados = 0
        dispositivo_mas_activo = None
        
        for dispositivo in self.dispositivos.values():
            if dispositivo.paquetes_procesados > max_procesados:
                max_procesados = dispositivo.paquetes_procesados
                dispositivo_mas_activo = dispositivo.nombre
        
        self.estadisticas_globales['dispositivo_mas_activo'] = dispositivo_mas_activo
        self.estadisticas_globales['max_paquetes_procesados'] = max_procesados
    
    def obtener_lista_dispositivos(self):
        """Retorna lista de todos los dispositivos"""
        lista = []
        for dispositivo in self.dispositivos.values():
            estado = 'online' if dispositivo.en_linea else 'offline'
            lista.append(f"  - {dispositivo.nombre} ({estado})")
        return lista
    
    def obtener_estadisticas_globales(self):
        """Retorna estadísticas globales de la red"""
        stats = self.estadisticas_globales.copy()
        
        # Calcular promedio de saltos
        if stats['paquetes_entregados'] > 0:
            stats['promedio_saltos'] = round(stats['total_saltos'] / stats['paquetes_entregados'], 1)
        else:
            stats['promedio_saltos'] = 0
        
        # Calcular total de paquetes enviados
        stats['paquetes_totales_enviados'] = sum(d.paquetes_enviados for d in self.dispositivos.values())
        
        return stats
    
    def obtener_conexiones(self):
        """Retorna lista de todas las conexiones"""
        return self.conexiones.obtener_lista()
    
    def validar_topologia(self):
        """Valida la consistencia de la topología de red"""
        errores = []
        
        for nombre, dispositivo in self.dispositivos.items():
            for int_nombre, interfaz in dispositivo.interfaces.items():
                vecinos = interfaz.obtener_vecinos()
                for vecino in vecinos:
                    # Verificar que la conexión sea bidireccional
                    if not vecino.vecinos.buscar(interfaz):
                        errores.append(f"Conexión unidireccional detectada: {nombre}:{int_nombre}")
        
        return errores
