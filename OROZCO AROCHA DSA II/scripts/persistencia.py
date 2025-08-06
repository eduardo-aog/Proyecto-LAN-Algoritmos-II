# Módulo 6: Persistencia de Configuración
# Guardar y cargar configuraciones en formato JSON

import json
import os
from datetime import datetime

class GestorPersistencia:
    """Maneja el guardado y carga de configuraciones"""
    
    def __init__(self, red):
        self.red = red
        self.archivo_por_defecto = "running-config.json"
    
    def guardar_configuracion(self, nombre_archivo=None):
        """Guarda la configuración actual en un archivo JSON"""
        if not nombre_archivo:
            nombre_archivo = self.archivo_por_defecto
        
        try:
            configuracion = self._extraer_configuracion()
            
            with open(nombre_archivo, 'w', encoding='utf-8') as archivo:
                json.dump(configuracion, archivo, indent=2, ensure_ascii=False)
            
            return f"Configuración guardada en {nombre_archivo}"
        
        except Exception as e:
            return f"Error al guardar configuración: {str(e)}"
    
    def cargar_configuracion(self, nombre_archivo):
        """Carga una configuración desde un archivo JSON"""
        if not os.path.exists(nombre_archivo):
            return f"Error: Archivo '{nombre_archivo}' no encontrado."
        
        try:
            with open(nombre_archivo, 'r', encoding='utf-8') as archivo:
                configuracion = json.load(archivo)
            
            resultado = self._aplicar_configuracion(configuracion)
            return f"Configuración cargada desde {nombre_archivo}\n{resultado}"
        
        except Exception as e:
            return f"Error al cargar configuración: {str(e)}"
    
    def _extraer_configuracion(self):
        """Extrae la configuración actual de la red"""
        configuracion = {
            'metadata': {
                'version': '1.0',
                'timestamp': datetime.now().isoformat(),
                'descripcion': 'Configuración del simulador de red LAN'
            },
            'dispositivos': {},
            'conexiones': []
        }
        
        # Extraer información de dispositivos
        for nombre, dispositivo in self.red.dispositivos.items():
            config_dispositivo = {
                'nombre': dispositivo.nombre,
                'tipo': dispositivo.tipo,
                'en_linea': dispositivo.en_linea,
                'interfaces': {}
            }
            
            # Extraer configuración de interfaces
            for int_nombre, interfaz in dispositivo.interfaces.items():
                config_interfaz = {
                    'nombre': interfaz.nombre,
                    'direccion_ip': interfaz.direccion_ip,
                    'activa': interfaz.activa
                }
                config_dispositivo['interfaces'][int_nombre] = config_interfaz
            
            configuracion['dispositivos'][nombre] = config_dispositivo
        
        # Extraer conexiones
        conexiones = self.red.obtener_conexiones()
        for conexion in conexiones:
            configuracion['conexiones'].append(conexion)
        
        return configuracion
    
    def _aplicar_configuracion(self, configuracion):
        """Aplica una configuración cargada a la red"""
        resultados = []
        
        # Limpiar red actual
        self.red.dispositivos.clear()
        self.red.conexiones = self.red.conexiones.__class__()  # Nueva lista enlazada vacía
        
        # Crear dispositivos
        for nombre, config_disp in configuracion['dispositivos'].items():
            if self.red.agregar_dispositivo(nombre, config_disp['tipo']):
                dispositivo = self.red.obtener_dispositivo(nombre)
                dispositivo.establecer_estado(config_disp['en_linea'])
                
                # Configurar interfaces
                for int_nombre, config_int in config_disp['interfaces'].items():
                    if int_nombre not in dispositivo.interfaces:
                        dispositivo.agregar_interfaz(int_nombre)
                    
                    interfaz = dispositivo.obtener_interfaz(int_nombre)
                    if config_int['direccion_ip']:
                        interfaz.asignar_ip(config_int['direccion_ip'])
                    
                    if config_int['activa']:
                        interfaz.activar()
                    else:
                        interfaz.desactivar()
                
                resultados.append(f"Dispositivo {nombre} creado y configurado")
        
        # Recrear conexiones
        for conexion in configuracion['conexiones']:
            # Parsear formato "dispositivo1:interfaz1 <-> dispositivo2:interfaz2"
            partes = conexion.split(' <-> ')
            if len(partes) == 2:
                disp1_int1 = partes[0].split(':')
                disp2_int2 = partes[1].split(':')
                
                if len(disp1_int1) == 2 and len(disp2_int2) == 2:
                    if self.red.conectar_dispositivos(disp1_int1[0], disp1_int1[1], 
                                                    disp2_int2[0], disp2_int2[1]):
                        resultados.append(f"Conexión restaurada: {conexion}")
        
        return "\n".join(resultados)
    
    def cargar_datos_prueba(self):
        """Carga datos de prueba por defecto"""
        datos_prueba = {
            'metadata': {
                'version': '1.0',
                'timestamp': datetime.now().isoformat(),
                'descripcion': 'Datos de prueba para el simulador'
            },
            'dispositivos': {
                'Router1': {
                    'nombre': 'Router1',
                    'tipo': 'router',
                    'en_linea': True,
                    'interfaces': {
                        'g0/0': {
                            'nombre': 'g0/0',
                            'direccion_ip': '192.168.1.1',
                            'activa': True
                        },
                        'g0/1': {
                            'nombre': 'g0/1',
                            'direccion_ip': '10.0.0.1',
                            'activa': True
                        }
                    }
                },
                'Switch1': {
                    'nombre': 'Switch1',
                    'tipo': 'switch',
                    'en_linea': True,
                    'interfaces': {
                        'g0/0': {
                            'nombre': 'g0/0',
                            'direccion_ip': None,
                            'activa': True
                        },
                        'g0/1': {
                            'nombre': 'g0/1',
                            'direccion_ip': None,
                            'activa': True
                        }
                    }
                },
                'PC1': {
                    'nombre': 'PC1',
                    'tipo': 'pc',
                    'en_linea': True,
                    'interfaces': {
                        'eth0': {
                            'nombre': 'eth0',
                            'direccion_ip': '192.168.1.10',
                            'activa': True
                        }
                    }
                },
                'PC2': {
                    'nombre': 'PC2',
                    'tipo': 'pc',
                    'en_linea': True,
                    'interfaces': {
                        'eth0': {
                            'nombre': 'eth0',
                            'direccion_ip': '10.0.0.10',
                            'activa': True
                        }
                    }
                }
            },
            'conexiones': [
                'Router1:g0/0 <-> Switch1:g0/0',
                'Switch1:g0/1 <-> PC1:eth0',
                'Router1:g0/1 <-> PC2:eth0'
            ]
        }
        
        # Guardar datos de prueba
        with open('datos_prueba.json', 'w', encoding='utf-8') as archivo:
            json.dump(datos_prueba, archivo, indent=2, ensure_ascii=False)
        
        # Aplicar configuración
        return self._aplicar_configuracion(datos_prueba)
    
    def listar_archivos_configuracion(self):
        """Lista todos los archivos de configuración disponibles"""
        archivos = []
        for archivo in os.listdir('.'):
            if archivo.endswith('.json') and 'config' in archivo.lower():
                archivos.append(archivo)
        
        if archivos:
            return "Archivos de configuración disponibles:\n" + "\n".join(f"  - {archivo}" for archivo in archivos)
        else:
            return "No se encontraron archivos de configuración."
