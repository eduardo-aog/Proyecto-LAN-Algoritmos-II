# Script para ejecutar el simulador con manejo de errores mejorado

import sys
import os

def verificar_dependencias():
    """Verifica que todos los módulos necesarios estén disponibles"""
    modulos_requeridos = [
        'estructuras_datos',
        'paquete', 
        'dispositivo',
        'red',
        'estadisticas',
        'persistencia',
        'cli',
        'main'
    ]
    
    modulos_faltantes = []
    
    for modulo in modulos_requeridos:
        try:
            __import__(modulo)
        except ImportError:
            modulos_faltantes.append(modulo)
    
    if modulos_faltantes:
        print("Error: Los siguientes módulos no se encontraron:")
        for modulo in modulos_faltantes:
            print(f"  - {modulo}.py")
        print("\nAsegúrese de que todos los archivos estén en el mismo directorio.")
        return False
    
    return True

def mostrar_instrucciones():
    """Muestra instrucciones básicas de uso"""
    instrucciones = """
=== INSTRUCCIONES DE USO ===

El simulador inicia con datos de prueba que incluyen:
- Router1 (con interfaces g0/0 y g0/1)
- Switch1 (con 4 puertos)
- PC1 y PC2 (con interfaces eth0)
- Firewall1 (con interfaces inside/outside)

COMANDOS BÁSICOS PARA EMPEZAR:
1. enable                    # Entrar a modo privilegiado
2. list_devices             # Ver dispositivos disponibles
3. show interfaces          # Ver interfaces del dispositivo actual
4. console PC1              # Cambiar a PC1
5. send 192.168.1.10 10.0.0.10 "Hola PC2"  # Enviar mensaje
6. tick                     # Procesar simulación
7. show statistics          # Ver estadísticas

EJEMPLO DE SESIÓN COMPLETA:
Router1> enable
Router1# console PC1
PC1> send 192.168.1.10 10.0.0.10 "Mensaje de prueba"
PC1> tick
PC1> console PC2
PC2> show history
PC2> console Router1
Router1# show statistics

Escriba 'help' en cualquier momento para ver todos los comandos.
Escriba 'quit' para salir del simulador.
    """
    print(instrucciones)

def main():
    """Función principal con manejo de errores"""
    print("Iniciando Simulador de Red LAN...")
    
    # Verificar dependencias
    if not verificar_dependencias():
        sys.exit(1)
    
    # Mostrar instrucciones
    mostrar_instrucciones()
    
    try:
        # Importar y ejecutar simulador
        from main import SimuladorRedLAN
        
        simulador = SimuladorRedLAN()
        simulador.ejecutar_cli()
        
    except KeyboardInterrupt:
        print("\n\nSimulador interrumpido por el usuario.")
    except Exception as e:
        print(f"\nError crítico: {e}")
        print("El simulador se cerrará.")
        sys.exit(1)
    
    print("Simulador finalizado correctamente.")

if __name__ == "__main__":
    main()
