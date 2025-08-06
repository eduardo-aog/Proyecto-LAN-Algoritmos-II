# Punto de entrada principal del simulador
# Inicializa todos los componentes y ejecuta el CLI

import os
import sys
from red import Red
from estadisticas import GestorEstadisticas
from persistencia import GestorPersistencia
from cli import ParserCLI

class SimuladorRedLAN:
    """Clase principal que orquesta todo el simulador"""
    
    def __init__(self):
        self.red = Red()
        self.gestor_estadisticas = GestorEstadisticas(self.red)
        self.gestor_persistencia = GestorPersistencia(self.red)
        self.parser_cli = ParserCLI(self.red, self.gestor_estadisticas, self.gestor_persistencia)
        self.ejecutando = True
    
    def inicializar(self):
        """Inicializa el simulador con datos por defecto"""
        print("=== SIMULADOR DE RED LAN - CLI ESTILO ROUTER ===")
        print("Universidad José Antonio Páez - Ingeniería en Computación")
        print("Cargando configuración inicial...")
        
        # Intentar cargar datos de prueba
        try:
            resultado = self.gestor_persistencia.cargar_datos_prueba()
            print("Datos de prueba cargados exitosamente:")
            print(resultado)
        except Exception as e:
            print(f"Error cargando datos de prueba: {e}")
            print("Continuando con configuración vacía...")
        
        print("\nSimulador iniciado. Escriba 'help' para ver comandos disponibles.")
        print("Escriba 'quit' para salir del simulador.\n")
    
    def ejecutar_cli(self):
        """Ejecuta el bucle principal del CLI"""
        self.inicializar()
        
        while self.ejecutando:
            try:
                # Mostrar prompt y leer comando
                prompt = self.parser_cli.obtener_prompt()
                comando = input(prompt).strip()
                
                if not comando:
                    continue
                
                # Procesar comando
                resultado = self.parser_cli.procesar_comando(comando)
                
                # Verificar si se debe salir
                if resultado == "QUIT":
                    self.ejecutando = False
                    print("Saliendo del simulador...")
                    break
                
                # Mostrar resultado
                if resultado:
                    print(resultado)
                
            except KeyboardInterrupt:
                print("\n\nInterrupción detectada. Saliendo del simulador...")
                self.ejecutando = False
            except EOFError:
                print("\nSaliendo del simulador...")
                self.ejecutando = False
            except Exception as e:
                print(f"Error inesperado: {e}")
                print("El simulador continuará ejecutándose...")
    
    def mostrar_banner_inicial(self):
        """Muestra el banner inicial del simulador"""
        banner = """
                 SIMULADOR DE RED LAN         
        """
        print(banner)

def main():
    """Función principal del programa"""
    simulador = SimuladorRedLAN()
    simulador.mostrar_banner_inicial()
    simulador.ejecutar_cli()

if __name__ == "__main__":
    main()
