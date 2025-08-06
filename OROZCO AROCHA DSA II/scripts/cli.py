# Módulo 4: Interfaz de Línea de Comandos
# Parser CLI con diferentes modos usando patrón comando

import re
from abc import ABC, abstractmethod

class Comando(ABC):
    """Clase base para implementar patrón comando"""
    
    @abstractmethod
    def ejecutar(self, argumentos, contexto):
        pass
    
    @abstractmethod
    def obtener_ayuda(self):
        pass

class ComandoEnable(Comando):
    def ejecutar(self, argumentos, contexto):
        contexto.cambiar_modo('privilegiado')
        return "Modo privilegiado activado"
    
    def obtener_ayuda(self):
        return "enable - Entra al modo privilegiado"

class ComandoDisable(Comando):
    def ejecutar(self, argumentos, contexto):
        contexto.cambiar_modo('usuario')
        return "Modo usuario activado"
    
    def obtener_ayuda(self):
        return "disable - Regresa al modo usuario"

class ComandoConfigureTerminal(Comando):
    def ejecutar(self, argumentos, contexto):
        if contexto.modo_actual != 'privilegiado':
            return "Error: Comando disponible solo en modo privilegiado"
        contexto.cambiar_modo('configuracion')
        return "Entrando modo configuración global"
    
    def obtener_ayuda(self):
        return "configure terminal - Entra al modo de configuración global"

class ComandoHostname(Comando):
    def ejecutar(self, argumentos, contexto):
        if contexto.modo_actual != 'configuracion':
            return "Error: Comando disponible solo en modo configuración"
        
        if not argumentos:
            return "Error: Especifique el nombre del dispositivo"
        
        nuevo_nombre = argumentos[0]
        if contexto.dispositivo_actual.cambiar_nombre(nuevo_nombre):
            contexto.nombre_dispositivo = nuevo_nombre
            return f"Nombre cambiado a {nuevo_nombre}"
        return "Error: Nombre inválido"
    
    def obtener_ayuda(self):
        return "hostname <nombre> - Cambia el nombre del dispositivo"

class ComandoInterface(Comando):
    def ejecutar(self, argumentos, contexto):
        if contexto.modo_actual != 'configuracion':
            return "Error: Comando disponible solo en modo configuración"
        
        if not argumentos:
            return "Error: Especifique el nombre de la interfaz"
        
        nombre_interfaz = argumentos[0]
        if not contexto.dispositivo_actual.obtener_interfaz(nombre_interfaz):
            contexto.dispositivo_actual.agregar_interfaz(nombre_interfaz)
        
        contexto.interfaz_actual = nombre_interfaz
        contexto.cambiar_modo('configuracion_interfaz')
        return f"Configurando interfaz {nombre_interfaz}"
    
    def obtener_ayuda(self):
        return "interface <nombre> - Entra al modo de configuración de interfaz"

class ComandoIpAddress(Comando):
    def ejecutar(self, argumentos, contexto):
        if contexto.modo_actual != 'configuracion_interfaz':
            return "Error: Comando disponible solo en modo configuración de interfaz"
        
        if not argumentos:
            return "Error: Especifique la dirección IP"
        
        ip = argumentos[0]
        if contexto.dispositivo_actual.configurar_interfaz_ip(contexto.interfaz_actual, ip):
            return f"IP {ip} asignada a {contexto.interfaz_actual}"
        return "Error: Dirección IP inválida"
    
    def obtener_ayuda(self):
        return "ip address <ip> - Asigna dirección IP a la interfaz"

class ComandoShutdown(Comando):
    def ejecutar(self, argumentos, contexto):
        if contexto.modo_actual != 'configuracion_interfaz':
            return "Error: Comando disponible solo en modo configuración de interfaz"
        
        if argumentos and argumentos[0] == 'no':
            if contexto.dispositivo_actual.activar_interfaz(contexto.interfaz_actual):
                return f"Interfaz {contexto.interfaz_actual} activada"
        else:
            if contexto.dispositivo_actual.desactivar_interfaz(contexto.interfaz_actual):
                return f"Interfaz {contexto.interfaz_actual} desactivada"
        
        return "Error al cambiar estado de interfaz"
    
    def obtener_ayuda(self):
        return "shutdown / no shutdown - Desactiva/activa la interfaz"

class ComandoExit(Comando):
    def ejecutar(self, argumentos, contexto):
        if contexto.modo_actual == 'configuracion_interfaz':
            contexto.cambiar_modo('configuracion')
            return "Saliendo de configuración de interfaz"
        elif contexto.modo_actual == 'configuracion':
            contexto.cambiar_modo('privilegiado')
            return "Saliendo de configuración global"
        else:
            return "Ya está en el modo base"
    
    def obtener_ayuda(self):
        return "exit - Retrocede un nivel de modo"

class ComandoEnd(Comando):
    def ejecutar(self, argumentos, contexto):
        contexto.cambiar_modo('privilegiado')
        return "Regresando a modo privilegiado"
    
    def obtener_ayuda(self):
        return "end - Sale directamente a modo privilegiado"

class ComandoConnect(Comando):
    def ejecutar(self, argumentos, contexto):
        if len(argumentos) < 4:
            return "Error: Uso: connect <interfaz1> <dispositivo2> <interfaz2>"
        
        interfaz1 = argumentos[0]
        dispositivo2 = argumentos[1]
        interfaz2 = argumentos[2]
        
        if contexto.red.conectar_dispositivos(contexto.nombre_dispositivo, interfaz1, dispositivo2, interfaz2):
            return f"Conexión establecida: {contexto.nombre_dispositivo}:{interfaz1} <-> {dispositivo2}:{interfaz2}"
        return "Error: No se pudo establecer la conexión"
    
    def obtener_ayuda(self):
        return "connect <interfaz1> <dispositivo2> <interfaz2> - Conecta dos interfaces"

class ComandoDisconnect(Comando):
    def ejecutar(self, argumentos, contexto):
        if len(argumentos) < 4:
            return "Error: Uso: disconnect <interfaz1> <dispositivo2> <interfaz2>"
        
        interfaz1 = argumentos[0]
        dispositivo2 = argumentos[1]
        interfaz2 = argumentos[2]
        
        if contexto.red.desconectar_dispositivos(contexto.nombre_dispositivo, interfaz1, dispositivo2, interfaz2):
            return f"Conexión eliminada: {contexto.nombre_dispositivo}:{interfaz1} <-> {dispositivo2}:{interfaz2}"
        return "Error: No se pudo eliminar la conexión"
    
    def obtener_ayuda(self):
        return "disconnect <interfaz1> <dispositivo2> <interfaz2> - Desconecta dos interfaces"

class ComandoSend(Comando):
    def ejecutar(self, argumentos, contexto):
        if len(argumentos) < 3:
            return "Error: Uso: send <ip_origen> <ip_destino> <mensaje> [ttl]"
        
        ip_origen = argumentos[0]
        ip_destino = argumentos[1]
        mensaje = argumentos[2]
        ttl = int(argumentos[3]) if len(argumentos) > 3 else 64
        
        if contexto.dispositivo_actual.enviar_paquete(ip_origen, ip_destino, mensaje, ttl):
            return "Paquete enviado exitosamente"
        return "Error: No se pudo enviar el paquete"
    
    def obtener_ayuda(self):
        return "send <ip_origen> <ip_destino> <mensaje> [ttl] - Envía un paquete"

class ComandoTick(Comando):
    def ejecutar(self, argumentos, contexto):
        paquetes = contexto.red.procesar_tick()
        if paquetes:
            resultado = ["Tick procesado:"]
            for paquete in paquetes:
                info = paquete.obtener_info_completa()
                if info['entregado']:
                    resultado.append(f"  ✓ Paquete {info['id']} entregado: {info['traza']}")
                elif info['descartado']:
                    resultado.append(f"  ✗ Paquete {info['id']} descartado: {info['razon_descarte']}")
                else:
                    resultado.append(f"  → Paquete {info['id']} en tránsito: TTL={info['ttl_actual']}")
            return "\n".join(resultado)
        return "Tick procesado - sin actividad"
    
    def obtener_ayuda(self):
        return "tick / process - Procesa un paso de simulación"

class ContextoCLI:
    """Contexto que mantiene el estado actual del CLI"""
    
    def __init__(self, red, gestor_estadisticas, gestor_persistencia):
        self.red = red
        self.gestor_estadisticas = gestor_estadisticas
        self.gestor_persistencia = gestor_persistencia
        self.modo_actual = 'usuario'
        self.nombre_dispositivo = 'Router1'
        self.interfaz_actual = None
        self.dispositivo_actual = None
        
        # Crear dispositivo por defecto si no existe
        if not self.red.obtener_dispositivo(self.nombre_dispositivo):
            self.red.agregar_dispositivo(self.nombre_dispositivo, 'router')
        
        self.dispositivo_actual = self.red.obtener_dispositivo(self.nombre_dispositivo)
    
    def cambiar_modo(self, nuevo_modo):
        """Cambia el modo actual del CLI"""
        self.modo_actual = nuevo_modo
        if nuevo_modo != 'configuracion_interfaz':
            self.interfaz_actual = None
    
    def obtener_prompt(self):
        """Genera el prompt según el modo actual"""
        if self.modo_actual == 'usuario':
            return f"{self.nombre_dispositivo}> "
        elif self.modo_actual == 'privilegiado':
            return f"{self.nombre_dispositivo}# "
        elif self.modo_actual == 'configuracion':
            return f"{self.nombre_dispositivo}(config)# "
        elif self.modo_actual == 'configuracion_interfaz':
            return f"{self.nombre_dispositivo}(config-if)# "
        return f"{self.nombre_dispositivo}> "

class ParserCLI:
    """Parser principal del CLI que maneja todos los comandos"""
    
    def __init__(self, red, gestor_estadisticas, gestor_persistencia):
        self.contexto = ContextoCLI(red, gestor_estadisticas, gestor_persistencia)
        self.comandos = self._inicializar_comandos()
    
    def _inicializar_comandos(self):
        """Inicializa el diccionario de comandos disponibles"""
        return {
            'enable': ComandoEnable(),
            'disable': ComandoDisable(),
            'configure': ComandoConfigureTerminal(),
            'hostname': ComandoHostname(),
            'interface': ComandoInterface(),
            'ip': ComandoIpAddress(),
            'shutdown': ComandoShutdown(),
            'no': ComandoShutdown(),  # Para "no shutdown"
            'exit': ComandoExit(),
            'end': ComandoEnd(),
            'connect': ComandoConnect(),
            'disconnect': ComandoDisconnect(),
            'send': ComandoSend(),
            'tick': ComandoTick(),
            'process': ComandoTick(),  # Alias para tick
        }
    
    def procesar_comando(self, linea_comando):
        """Procesa una línea de comando completa"""
        if not linea_comando.strip():
            return ""
        
        # Parsear comando y argumentos
        partes = linea_comando.strip().split()
        comando_principal = partes[0].lower()
        argumentos = partes[1:]
        
        # Manejar comandos especiales
        if comando_principal == 'show':
            return self._manejar_show(argumentos)
        elif comando_principal == 'save':
            return self._manejar_save(argumentos)
        elif comando_principal == 'load':
            return self._manejar_load(argumentos)
        elif comando_principal == 'list_devices':
            return self._manejar_list_devices()
        elif comando_principal == 'set_device_status':
            return self._manejar_set_device_status(argumentos)
        elif comando_principal == 'console':
            return self._manejar_console(argumentos)
        elif comando_principal == 'help':
            return self._mostrar_ayuda()
        elif comando_principal == 'quit' or comando_principal == 'exit':
            if self.contexto.modo_actual == 'usuario':
                return "QUIT"
        
        # Manejar comandos compuestos
        if comando_principal == 'configure' and argumentos and argumentos[0] == 'terminal':
            comando_principal = 'configure'
            argumentos = ['terminal']
        elif comando_principal == 'no' and argumentos:
            # Manejar "no shutdown"
            if argumentos[0] == 'shutdown':
                argumentos = ['no'] + argumentos
                comando_principal = 'shutdown'
        elif comando_principal == 'ip' and argumentos and argumentos[0] == 'address':
            # Manejar "ip address"
            if len(argumentos) > 1:
                argumentos = argumentos[1:]  # Remover 'address'
                comando_principal = 'ip'
        
        # Ejecutar comando
        if comando_principal in self.comandos:
            try:
                return self.comandos[comando_principal].ejecutar(argumentos, self.contexto)
            except Exception as e:
                return f"Error ejecutando comando: {str(e)}"
        else:
            return f"Comando no reconocido: {comando_principal}"
    
    def _manejar_show(self, argumentos):
        """Maneja los comandos show"""
        if not argumentos:
            return "Error: Especifique qué mostrar (history, queue, interfaces, statistics)"
        
        subcomando = argumentos[0].lower()
        
        if subcomando == 'history':
            dispositivo = argumentos[1] if len(argumentos) > 1 else self.contexto.nombre_dispositivo
            return self.contexto.gestor_estadisticas.mostrar_historial_dispositivo(dispositivo)
        
        elif subcomando == 'queue':
            dispositivo = argumentos[1] if len(argumentos) > 1 else self.contexto.nombre_dispositivo
            return self.contexto.gestor_estadisticas.mostrar_colas_dispositivo(dispositivo)
        
        elif subcomando == 'interfaces':
            dispositivo = argumentos[1] if len(argumentos) > 1 else self.contexto.nombre_dispositivo
            return self.contexto.gestor_estadisticas.mostrar_interfaces_dispositivo(dispositivo)
        
        elif subcomando == 'statistics':
            return self.contexto.gestor_estadisticas.mostrar_estadisticas_globales()
        
        else:
            return f"Subcomando show no reconocido: {subcomando}"
    
    def _manejar_save(self, argumentos):
        """Maneja el comando save"""
        if argumentos and argumentos[0] == 'running-config':
            archivo = argumentos[1] if len(argumentos) > 1 else None
            return self.contexto.gestor_persistencia.guardar_configuracion(archivo)
        return "Error: Uso: save running-config [archivo]"
    
    def _manejar_load(self, argumentos):
        """Maneja el comando load"""
        if len(argumentos) >= 2 and argumentos[0] == 'config':
            return self.contexto.gestor_persistencia.cargar_configuracion(argumentos[1])
        return "Error: Uso: load config <archivo>"
    
    def _manejar_list_devices(self):
        """Maneja el comando list_devices"""
        dispositivos = self.contexto.red.obtener_lista_dispositivos()
        return "Dispositivos en la red:\n" + "\n".join(dispositivos)
    
    def _manejar_set_device_status(self, argumentos):
        """Maneja el comando set_device_status"""
        if len(argumentos) < 2:
            return "Error: Uso: set_device_status <dispositivo> <online|offline>"
        
        dispositivo = argumentos[0]
        estado = argumentos[1].lower()
        
        if estado not in ['online', 'offline']:
            return "Error: Estado debe ser 'online' u 'offline'"
        
        en_linea = estado == 'online'
        if self.contexto.red.establecer_estado_dispositivo(dispositivo, en_linea):
            return f"Dispositivo {dispositivo} establecido como {estado}"
        return f"Error: Dispositivo {dispositivo} no encontrado"
    
    def _manejar_console(self, argumentos):
        """Maneja el comando console para cambiar de dispositivo"""
        if not argumentos:
            return "Error: Especifique el dispositivo"
        
        nombre_dispositivo = argumentos[0]
        dispositivo = self.contexto.red.obtener_dispositivo(nombre_dispositivo)
        
        if dispositivo:
            self.contexto.nombre_dispositivo = nombre_dispositivo
            self.contexto.dispositivo_actual = dispositivo
            self.contexto.cambiar_modo('usuario')
            return f"Conectado a {nombre_dispositivo}"
        return f"Error: Dispositivo {nombre_dispositivo} no encontrado"
    
    def _mostrar_ayuda(self):
        """Muestra la ayuda de comandos disponibles"""
        ayuda = ["\n=== COMANDOS DISPONIBLES ==="]
        
        # Comandos básicos
        ayuda.append("\nComandos básicos:")
        ayuda.append("  enable - Entra al modo privilegiado")
        ayuda.append("  disable - Regresa al modo usuario")
        ayuda.append("  exit - Retrocede un nivel de modo")
        ayuda.append("  end - Sale directamente a modo privilegiado")
        ayuda.append("  help - Muestra esta ayuda")
        ayuda.append("  quit - Sale del simulador")
        
        # Comandos de configuración
        ayuda.append("\nComandos de configuración:")
        ayuda.append("  configure terminal - Entra al modo de configuración")
        ayuda.append("  hostname <nombre> - Cambia nombre del dispositivo")
        ayuda.append("  interface <nombre> - Configura una interfaz")
        ayuda.append("  ip address <ip> - Asigna IP a la interfaz")
        ayuda.append("  shutdown / no shutdown - Desactiva/activa interfaz")
        
        # Comandos de red
        ayuda.append("\nComandos de red:")
        ayuda.append("  connect <int1> <disp2> <int2> - Conecta interfaces")
        ayuda.append("  disconnect <int1> <disp2> <int2> - Desconecta interfaces")
        ayuda.append("  list_devices - Lista todos los dispositivos")
        ayuda.append("  set_device_status <disp> <online|offline> - Cambia estado")
        ayuda.append("  console <dispositivo> - Cambia a otro dispositivo")
        
        # Comandos de comunicación
        ayuda.append("\nComandos de comunicación:")
        ayuda.append("  send <origen> <destino> <mensaje> [ttl] - Envía paquete")
        ayuda.append("  tick / process - Procesa un paso de simulación")
        
        # Comandos de información
        ayuda.append("\nComandos de información:")
        ayuda.append("  show history [dispositivo] - Muestra historial")
        ayuda.append("  show queue [dispositivo] - Muestra colas")
        ayuda.append("  show interfaces [dispositivo] - Muestra interfaces")
        ayuda.append("  show statistics - Muestra estadísticas globales")
        
        # Comandos de persistencia
        ayuda.append("\nComandos de persistencia:")
        ayuda.append("  save running-config [archivo] - Guarda configuración")
        ayuda.append("  load config <archivo> - Carga configuración")
        
        return "\n".join(ayuda)
    
    def obtener_prompt(self):
        """Obtiene el prompt actual"""
        return self.contexto.obtener_prompt()
    
    def obtener_modo_actual(self):
        """Obtiene el modo actual del CLI"""
        return self.contexto.modo_actual
