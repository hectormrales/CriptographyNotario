"""
Script de utilidad para generar un par de claves manualmente
y exportarlas en diferentes formatos.
Soporta múltiples curvas elípticas.
"""

import sys
import os

# Agregar el directorio shared al path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from shared.crypto_utils import NotarioCrypto, CURVAS_SOPORTADAS


def main():
    print("=" * 60)
    print("Generador de Claves ECDSA - Notario Digital")
    print("=" * 60)
    print()
    
    # Mostrar curvas disponibles
    print("Curvas elípticas disponibles:")
    print()
    for i, (codigo, info) in enumerate(CURVAS_SOPORTADAS.items(), 1):
        print(f"{i}. {info['nombre']}")
        print(f"   {info['descripcion']}")
        print()
    
    # Seleccionar curva
    while True:
        try:
            opcion = input(f"Selecciona una curva (1-{len(CURVAS_SOPORTADAS)}) [Por defecto: 1]: ").strip()
            if opcion == "":
                opcion = "1"
            
            idx = int(opcion) - 1
            if 0 <= idx < len(CURVAS_SOPORTADAS):
                curva_seleccionada = list(CURVAS_SOPORTADAS.keys())[idx]
                break
            else:
                print("❌ Opción inválida")
        except ValueError:
            print("❌ Por favor ingresa un número válido")
    
    print(f"✅ Curva seleccionada: {CURVAS_SOPORTADAS[curva_seleccionada]['nombre']}")
    print()
    
    # Crear instancia con la curva seleccionada
    crypto = NotarioCrypto(curva=curva_seleccionada)
    
    # Generar claves
    print(f"🔑 Generando par de claves {curva_seleccionada}...")
    crypto.generar_par_claves()
    print("✅ Claves generadas exitosamente")
    print()
    
    # Preguntar si cifrar con contraseña
    usar_password = input("¿Deseas proteger la clave privada con contraseña? (s/n): ").lower()
    password = None
    
    if usar_password == 's':
        password = input("Ingresa la contraseña: ")
        confirm = input("Confirma la contraseña: ")
        
        if password != confirm:
            print("❌ Las contraseñas no coinciden")
            return
        
        print("🔒 Se usará contraseña para cifrar la clave privada")
    
    # Rutas
    keys_dir = os.path.join(os.path.dirname(__file__), '..', 'keys')
    os.makedirs(keys_dir, exist_ok=True)
    
    # Incluir nombre de curva en el archivo
    private_path = os.path.join(keys_dir, f'notario_private_{curva_seleccionada.lower()}.pem')
    public_path = os.path.join(keys_dir, f'notario_public_{curva_seleccionada.lower()}.pem')
    
    # Guardar claves
    print()
    print("💾 Guardando claves...")
    crypto.guardar_clave_privada(private_path, password)
    crypto.guardar_clave_publica(public_path)
    
    print(f"✅ Clave privada guardada en: {private_path}")
    print(f"✅ Clave pública guardada en: {public_path}")
    print()
    
    # Mostrar clave pública
    print("=" * 60)
    print("Clave Pública (puede compartirse):")
    print("=" * 60)
    print(crypto.exportar_clave_publica_str())
    
    print("=" * 60)
    print("✅ Proceso completado")
    print()
    print("⚠️  IMPORTANTE:")
    print("   - NUNCA compartas la clave privada")
    print("   - Guarda la clave privada en un lugar seguro")
    print("   - La clave pública puede compartirse libremente")
    print(f"   - Estas claves usan la curva: {curva_seleccionada}")
    print("=" * 60)


if __name__ == "__main__":
    main()
