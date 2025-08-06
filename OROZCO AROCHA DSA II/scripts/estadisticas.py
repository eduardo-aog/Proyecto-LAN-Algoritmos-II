# Módulo 5: Estadísticas y Reportes
# Manejo de estadísticas y generación de reportes

class GestorEstadisticas:
    """Gestiona la recolección y presentación de estadísticas"""
    
    def __init__(self, red):
        self.red = red
    
    def mostrar_historial_dispositivo(self, nombre_dispositivo):
        """Muestra el historial de paquetes recibidos por un dispositivo"""
        dispositivo = self.red.obtener_dispositivo(nombre_dispositivo)
        if not dispositivo:
            return f"Error: Dispositivo '{nombre_dispositivo}' no encontrado."
        
        historial = dispositivo.obtener_historial()
        if not historial:
            return f"No hay historial de paquetes para {nombre_dispositivo}."
        
        resultado = [f"\nHistorial de {nombre_dispositivo}:"]
        for i, paquete in enumerate(historial, 1):
            info = paquete.obtener_info_completa()
            ttl_info = f"TTL al llegar: {info['ttl_actual']}" if not info['descartado'] else "TTL expirado"
            resultado.append(f"{i}) De {info['origen']} a {info['destino']}: \"{info['contenido']}\" | {ttl_info} | Ruta: {info['traza']}")
        
        return "\n".join(resultado)
    
    def mostrar_colas_dispositivo(self, nombre_dispositivo):
        """Muestra el estado de las colas de un dispositivo"""
        dispositivo = self.red.obtener_dispositivo(nombre_dispositivo)
        if not dispositivo:
            return f"Error: Dispositivo '{nombre_dispositivo}' no encontrado."
        
        colas_info = dispositivo.obtener_colas_info()
        resultado = [f"\nEstado de colas de {nombre_dispositivo}:"]
        
        for interfaz, colas in colas_info.items():
            resultado.append(f"\nInterfaz {interfaz}:")
            
            # Cola de entrada
            if colas['entrada']:
                resultado.append("  Cola de entrada:")
                for paquete in colas['entrada']:
                    resultado.append(f"    - {paquete}")
            else:
                resultado.append("  Cola de entrada: vacía")
            
            # Cola de salida
            if colas['salida']:
                resultado.append("  Cola de salida:")
                for paquete in colas['salida']:
                    resultado.append(f"    - {paquete}")
            else:
                resultado.append("  Cola de salida: vacía")
        
        return "\n".join(resultado)
    
    def mostrar_interfaces_dispositivo(self, nombre_dispositivo):
        """Muestra información de las interfaces de un dispositivo"""
        dispositivo = self.red.obtener_dispositivo(nombre_dispositivo)
        if not dispositivo:
            return f"Error: Dispositivo '{nombre_dispositivo}' no encontrado."
        
        interfaces_info = dispositivo.obtener_info_interfaces()
        resultado = [f"\nInterfaces de {nombre_dispositivo}:"]
        
        for nombre, info in interfaces_info.items():
            estado_color = "UP" if info['estado'] == 'up' else "DOWN"
            resultado.append(f"\n{nombre}:")
            resultado.append(f"  IP: {info['ip']}")
            resultado.append(f"  Estado: {estado_color}")
            resultado.append(f"  Vecinos conectados: {info['vecinos']}")
            resultado.append(f"  Cola entrada: {info['cola_entrada']} paquetes")
            resultado.append(f"  Cola salida: {info['cola_salida']} paquetes")
        
        return "\n".join(resultado)
    
    def mostrar_estadisticas_globales(self):
        """Muestra estadísticas globales de la red"""
        stats = self.red.obtener_estadisticas_globales()
        
        resultado = ["\n=== ESTADÍSTICAS DE RED ==="]
        resultado.append(f"Total paquetes enviados: {stats['paquetes_totales_enviados']}")
        resultado.append(f"Paquetes entregados: {stats['paquetes_entregados']}")
        resultado.append(f"Descartados (TTL): {stats['paquetes_descartados_ttl']}")
        resultado.append(f"Descartados (sin ruta): {stats['paquetes_descartados_ruta']}")
        resultado.append(f"Promedio de saltos: {stats['promedio_saltos']}")
        
        if stats['dispositivo_mas_activo']:
            resultado.append(f"Dispositivo más activo: {stats['dispositivo_mas_activo']} ({stats['max_paquetes_procesados']} paquetes procesados)")
        
        # Estadísticas por dispositivo
        resultado.append("\n=== ESTADÍSTICAS POR DISPOSITIVO ===")
        for dispositivo in self.red.dispositivos.values():
            stats_disp = dispositivo.obtener_estadisticas()
            resultado.append(f"\n{stats_disp['nombre']} ({stats_disp['tipo']}):")
            resultado.append(f"  Estado: {stats_disp['estado']}")
            resultado.append(f"  Interfaces: {stats_disp['interfaces']}")
            resultado.append(f"  Paquetes enviados: {stats_disp['paquetes_enviados']}")
            resultado.append(f"  Paquetes procesados: {stats_disp['paquetes_procesados']}")
            resultado.append(f"  Paquetes descartados: {stats_disp['paquetes_descartados']}")
            resultado.append(f"  Historial recibidos: {stats_disp['historial_size']}")
        
        return "\n".join(resultado)
    
    def generar_reporte_topologia(self):
        """Genera un reporte de la topología de red"""
        resultado = ["\n=== TOPOLOGÍA DE RED ==="]
        
        # Lista de dispositivos
        resultado.append("\nDispositivos:")
        lista_dispositivos = self.red.obtener_lista_dispositivos()
        resultado.extend(lista_dispositivos)
        
        # Lista de conexiones
        resultado.append("\nConexiones:")
        conexiones = self.red.obtener_conexiones()
        if conexiones:
            for conexion in conexiones:
                resultado.append(f"  - {conexion}")
        else:
            resultado.append("  - No hay conexiones establecidas")
        
        # Validación de topología
        errores = self.red.validar_topologia()
        if errores:
            resultado.append("\nErrores de topología detectados:")
            for error in errores:
                resultado.append(f"  - {error}")
        else:
            resultado.append("\nTopología válida - sin errores detectados")
        
        return "\n".join(resultado)
